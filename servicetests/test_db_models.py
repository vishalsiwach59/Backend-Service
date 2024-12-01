import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backendservice.databaseModels.database import Base
from backendservice.databaseModels.models import User, Organization, Cluster, Deployment

# Create an in-memory SQLite engine for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# Create the engine and sessionmaker for testing
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def session():
    # Create the tables in the database
    Base.metadata.create_all(bind=engine)
    
    # Create a session
    db_session = SessionLocal()
    
    yield db_session
    
    # Cleanup after tests
    db_session.close()
    Base.metadata.drop_all(bind=engine)

def test_create_user_and_organization(session):
    # Create an organization
    org = Organization(name="Test Org", invite_code="abc123")
    session.add(org)
    session.commit()
    
    # Create a user
    user = User(username="test_user", password_hash="hashed_password", organization_id=org.id)
    session.add(user)
    session.commit()
    
    # Query the organization and user
    fetched_user = session.query(User).filter_by(username="test_user").first()
    fetched_org = session.query(Organization).filter_by(name="Test Org").first()
    
    assert fetched_user is not None
    assert fetched_org is not None
    assert fetched_user.organization == fetched_org
    assert fetched_user.username == "test_user"
    assert fetched_user.organization_id == org.id

def test_organization_users_relationship(session):
    # Create an organization and add users
    org = Organization(name="Org with Users", invite_code="xyz456")
    user1 = User(username="user1", password_hash="hash1", organization=org)
    user2 = User(username="user2", password_hash="hash2", organization=org)
    
    session.add(org)
    session.add(user1)
    session.add(user2)
    session.commit()
    
    # Query organization and check its users
    fetched_org = session.query(Organization).filter_by(name="Org with Users").first()
    users_in_org = fetched_org.users
    
    assert len(users_in_org) == 2
    assert users_in_org[0].username == "user1"
    assert users_in_org[1].username == "user2"

def test_create_cluster(session):
    # Create an organization
    org = Organization(name="Cluster Org", invite_code="cluster123")
    session.add(org)
    session.commit()
    
    # Create a cluster in that organization
    cluster = Cluster(name="Cluster1", ram=16, cpu=4, gpu=2, organization_id=org.id)
    session.add(cluster)
    session.commit()
    
    # Query and assert the cluster
    fetched_cluster = session.query(Cluster).filter_by(name="Cluster1").first()
    assert fetched_cluster is not None
    assert fetched_cluster.organization_id == org.id
    assert fetched_cluster.ram == 16
    assert fetched_cluster.cpu == 4
    assert fetched_cluster.gpu == 2

def test_create_deployment(session):
    # Create organization and cluster
    org = Organization(name="Deployment Org", invite_code="deploy123")
    cluster = Cluster(name="Cluster2", ram=32, cpu=8, gpu=4, organization_id=org.id)
    session.add(org)
    session.add(cluster)
    session.commit()
    
    # Create a deployment
    deployment = Deployment(
        cluster_id=cluster.id,
        organization_id=org.id,
        image_path="path/to/image",
        ram=8,
        cpu=2,
        gpu=1,
        status="queued",
        priority=1
    )
    session.add(deployment)
    session.commit()
    
    # Query and assert the deployment
    fetched_deployment = session.query(Deployment).filter_by(cluster_id=cluster.id).first()
    assert fetched_deployment is not None
    assert fetched_deployment.status == "queued"
    assert fetched_deployment.priority == 1
    assert fetched_deployment.cluster_id == cluster.id
    assert fetched_deployment.organization_id == org.id

def test_update_user_role(session):
    # Create an organization and a user
    org = Organization(name="Update Role Org", invite_code="role123")
    user = User(username="user_to_update", password_hash="password", organization=org)
    session.add(org)
    session.add(user)
    session.commit()
    
    # Update the user's role
    user.role = "Admin"
    session.commit()
    
    # Query and assert the updated role
    updated_user = session.query(User).filter_by(username="user_to_update").first()
    assert updated_user.role == "Admin"
