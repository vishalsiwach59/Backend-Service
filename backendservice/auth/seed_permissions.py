from sqlalchemy.orm import Session
from backendservice.databaseModels.models import Permission

def seed_permissions(db: Session):
    permissions = [
        {"role": "Admin", "resource": "organizations", "action": "create"},
        {"role": "Admin", "resource": "organizations", "action": "read"},
        {"role": "Admin", "resource": "clusters", "action": "create"},
        {"role": "Admin", "resource": "clusters", "action": "read"},
        {"role": "Developer", "resource": "deployments", "action": "create"},
        {"role": "Developer", "resource": "deployments", "action": "read"},
        {"role": "Viewer", "resource": "clusters", "action": "read"},
        {"role": "Viewer", "resource": "deployments", "action": "read"},
    ]
    
    # Check and add permissions to the database if they don't already exist
    for permission in permissions:
        if not db.query(Permission).filter_by(**permission).first():
            db.add(Permission(**permission))
    db.commit()