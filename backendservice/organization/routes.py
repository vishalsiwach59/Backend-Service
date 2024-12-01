from fastapi import  Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from backendservice.databaseModels import database, models
from fastapi import HTTPException, Depends
from backendservice.auth.auth import get_current_user
from backendservice.databaseModels import models
from backendservice.databaseModels.schemas import *

router = APIRouter()

@router.post("/join_organization")
def join_organization(
    request: JoinOrganizationRequest,
    db: Session = Depends(database.get_db),
    user: models.User = Depends(get_current_user),
):
    
    # Fetch the organization using the invite code
    organization = db.query(models.Organization).filter(models.Organization.invite_code == request.invite_code).first()
    if not organization:
        raise HTTPException(status_code=400, detail="Invalid invite code")
    
    # Check if the user is already part of an organization
    if user.organization_id:
        if user.organization_id == organization.id:
            return {"message": f"User {user.username} is already part of the organization {organization.name}"}
        raise HTTPException(status_code=400, detail="User is already part of another organization")
    
    # Maintain role hierarchy: don't overwrite a higher role
    if not user.role or user.role.lower() == "viewer":
        user.role = "viewer"  # Assign "viewer" role only if the user doesn't have a higher role

    user.organization_id = organization.id  # Assign the organization
    db.commit()
    db.refresh(user)

    return {"message": f"User {user.username} added to organization {organization.name} with role {user.role}"}


@router.post("/create_organization")
def create_organization(organization: OrganizationCreate, db: Session = Depends(database.get_db), user: models.User = Depends(get_current_user)):
    # Only admins can create organizations
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    existing_org = db.query(models.Organization).filter(models.Organization.name == organization.name).first()
    if existing_org:
        raise HTTPException(status_code=400, detail="Organization name already taken")

    new_org = models.Organization(name=organization.name, invite_code=organization.invite_code)
    db.add(new_org)
    db.commit()
    db.refresh(new_org)
    return {"message": f"Organization {new_org.name} created successfully"}