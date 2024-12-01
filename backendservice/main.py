from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from backendservice.databaseModels import database, models
from fastapi import HTTPException, Depends
from backendservice.auth.auth import get_current_user
from backendservice.databaseModels import models
from backendservice.databaseModels.schemas import *
from backendservice.auth.routes import router as auth_router
from backendservice.organization.routes import router as org_router
from backendservice.clusters.routes import router as clusters_router
from backendservice.deployments.routes import router as deployments_router

app = FastAPI()

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(org_router, prefix="/organizations", tags=["Organizations"])
app.include_router(clusters_router,  tags=["Clusters"])
app.include_router(deployments_router,  tags=["Clusters"])

@app.post("/assign_role_to_user")
def assign_role_to_user(org_id: int, username: str, role: str, db: Session = Depends(database.get_db), user: models.User = Depends(get_current_user)):
    # Only admins can assign roles
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    organization = db.query(models.Organization).filter(models.Organization.id == org_id).first()
    if not organization:
        raise HTTPException(status_code=400, detail="Organization not found")
    
    target_user = db.query(models.User).filter(models.User.username == username).first()
    if not target_user:
        raise HTTPException(status_code=400, detail="User not found")
    
    if target_user.organization_id != organization.id:
        raise HTTPException(status_code=400, detail="User not in this organization")
    
    target_user.role = role  # Assign the new role
    db.commit()
    db.refresh(target_user)
    return {"message": f"User {target_user.username} role updated to {role}"}

# This is the example RBAC role-based access control
def role_based_access_control(user: models.User, required_role: str):
    if user.role != required_role:
        raise HTTPException(status_code=403, detail=f"Insufficient permissions. Required role: {required_role}")

