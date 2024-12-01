from fastapi import  Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from backendservice.databaseModels import database, models
from fastapi import HTTPException, Depends
from typing import List
from backendservice.auth.auth import get_current_user
from backendservice.databaseModels import models
from backendservice.databaseModels.schemas import *

router = APIRouter()

@router.post("/clusters", response_model=ClusterResponse)
def create_cluster(cluster: ClusterCreate, db: Session = Depends(database.get_db), user: models.User = Depends(get_current_user)):
    # Check if user is part of an organization and has admin permissions
    if not user.organization_id:
        raise HTTPException(status_code=403, detail="User is not part of any organization")
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    # Ensure cluster name is unique within the organization
    existing_cluster = db.query(models.Cluster).filter(
        models.Cluster.name == cluster.name,
        models.Cluster.organization_id == user.organization_id
    ).first()
    if existing_cluster:
        raise HTTPException(status_code=400, detail="Cluster name already taken in your organization")
    
    # Create the cluster
    new_cluster = models.Cluster(
        name=cluster.name,
        ram=cluster.ram,
        cpu=cluster.cpu,
        gpu=cluster.gpu,
        organization_id=user.organization_id
    )
    db.add(new_cluster)
    db.commit()
    db.refresh(new_cluster)
    return new_cluster

@router.get("/clusters", response_model=List[ClusterResponse])
def get_clusters(db: Session = Depends(database.get_db), user: models.User = Depends(get_current_user)):
    # Ensure the user is part of an organization
    if not user.organization_id:
        raise HTTPException(status_code=403, detail="User is not part of any organization")

    clusters = db.query(models.Cluster).filter(models.Cluster.organization_id == user.organization_id).all()
    return clusters

