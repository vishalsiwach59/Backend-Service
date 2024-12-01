from sqlalchemy import Column, Integer, String, ForeignKey, Float, Boolean, DateTime
from sqlalchemy.orm import relationship
from backendservice.databaseModels.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    role = Column(String, default="Viewer")  # Admin, Developer, Viewer
    
    # Adding the reverse relationship to Organization
    organization = relationship("Organization", back_populates="users")

class Organization(Base):
    __tablename__ = "organizations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    invite_code = Column(String, unique=True, nullable=False)
    users = relationship("User", back_populates="organization")
    clusters = relationship("Cluster", back_populates="organization")


class Cluster(Base):
    __tablename__ = "clusters"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    ram = Column(Integer, nullable=False)
    cpu = Column(Integer, nullable=False)
    gpu = Column(Integer, nullable=False)
    allocated_ram = Column(Integer, default=0)
    allocated_cpu = Column(Integer, default=0)
    allocated_gpu = Column(Integer, default=0)
    organization_id = Column(Integer, ForeignKey("organizations.id"))

    organization = relationship("Organization", back_populates="clusters")
    deployments = relationship("Deployment", back_populates="cluster")

class Deployment(Base):
    __tablename__ = "deployments"

    id = Column(Integer, primary_key=True, index=True)
    cluster_id = Column(Integer, ForeignKey("clusters.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    image_path = Column(String, nullable=False)
    ram = Column(Integer, nullable=False)
    cpu = Column(Integer, nullable=False)
    gpu = Column(Integer, nullable=False)
    status = Column(String, default="queued")  
    priority = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    cluster = relationship("Cluster", back_populates="deployments")

