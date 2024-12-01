from fastapi import  Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from backendservice.databaseModels import database, models
from fastapi import HTTPException, Depends
from typing import List
from backendservice.auth.auth import get_current_user
from backendservice.databaseModels import models
from backendservice.databaseModels.schemas import *
from redis import Redis
from rq import Queue
from fastapi import BackgroundTasks

redis_conn = Redis.from_url("redis://redis:6379/0")
queue = Queue("default", connection=redis_conn)

router = APIRouter()

def process_deployment_task(cluster_id):
    from backendservice.databaseModels import database, models
    from sqlalchemy.orm import Session

    # Access database session
    db_gen = database.get_db()
    db: Session = next(db_gen)  # Get the actual Session instance

    try:
        # Fetch cluster details
        cluster = db.query(models.Cluster).filter(models.Cluster.id == cluster_id).first()

        # Fetch queued deployments sorted by priority
        queued_deployments = db.query(models.Deployment).filter(
            models.Deployment.cluster_id == cluster_id,
            models.Deployment.status == "queued"
        ).order_by(models.Deployment.priority.desc(), models.Deployment.id).all()

        for deployment in queued_deployments:
            # Check if resources are available
            if cluster.ram >= cluster.allocated_ram + deployment.ram and \
                cluster.cpu >= cluster.allocated_cpu + deployment.cpu and \
                cluster.gpu >= cluster.allocated_gpu + deployment.gpu:
                # Allocate resources and start deployment
                cluster.allocated_ram += deployment.ram
                cluster.allocated_cpu += deployment.cpu
                cluster.allocated_gpu += deployment.gpu
                deployment.status = "running"
                db.commit()
            else:
                # Stop processing if resources are insufficient for remaining deployments
                break
    finally:
        db_gen.close()  # Ensure the session is properly closed


@router.post("/clusters/{cluster_id}/process_queue")
def enqueue_queued_deployments(cluster_id: int, db: Session = Depends(database.get_db)):
    # Enqueue cluster-wide task to process deployments
    queue.enqueue(process_deployment_task, cluster_id)
    return {"message": "Processing queued deployments initiated"}


@router.post("/clusters/{cluster_id}/deploy")
def create_deployment(
    cluster_id: int,
    request: DeploymentCreate,
    db: Session = Depends(database.get_db),
    user: models.User = Depends(get_current_user),
):
    # Ensure user is part of an organization
    if not user.organization_id:
        raise HTTPException(status_code=403, detail="User is not part of any organization")
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    cluster = db.query(models.Cluster).filter(
        models.Cluster.id == cluster_id,
        models.Cluster.organization_id == user.organization_id
    ).first()

    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")

    status = "queued"
    priority = request.priority if request.priority else 0  # Default priority

    # Create the deployment record
    new_deployment = models.Deployment(
        cluster_id=cluster_id,
        organization_id=user.organization_id,
        image_path=request.image_path,
        ram=request.ram,
        cpu=request.cpu,
        gpu=request.gpu,
        status=status,
        priority=priority
    )
    db.add(new_deployment)
    db.commit()
    db.refresh(new_deployment)

    # Enqueue the deployment processing task
    queue.enqueue(process_deployment_task, cluster_id)

    return {"message": "Deployment queued successfully", "deployment": new_deployment}



@router.get("/clusters/{cluster_id}/deployments")
def get_deployments(
    cluster_id: int,
    db: Session = Depends(database.get_db),
    user: models.User = Depends(get_current_user),
):
    # Ensure the user is part of an organization
    if not user.organization_id:
        raise HTTPException(status_code=403, detail="User is not part of any organization")

    cluster = db.query(models.Cluster).filter(models.Cluster.id == cluster_id, models.Cluster.organization_id == user.organization_id).first()
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")

    deployments = db.query(models.Deployment).filter(models.Deployment.cluster_id == cluster_id).all()
    return {"deployments": deployments}

@router.delete("/clusters/{cluster_id}/deployments/{deployment_id}")
def delete_deployment(
    cluster_id: int,
    deployment_id: int,
    db: Session = Depends(database.get_db),
    user: models.User = Depends(get_current_user),
):
    # Ensure the user is part of an organization
    if not user.organization_id:
        raise HTTPException(status_code=403, detail="User is not part of any organization")

    cluster = db.query(models.Cluster).filter(
        models.Cluster.id == cluster_id,
        models.Cluster.organization_id == user.organization_id
    ).first()

    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")

    deployment = db.query(models.Deployment).filter(
        models.Deployment.id == deployment_id,
        models.Deployment.cluster_id == cluster_id,
        models.Deployment.status == "running"
    ).first()

    if not deployment:
        raise HTTPException(status_code=404, detail="Running deployment not found")

    # Free up cluster resources
    cluster.allocated_ram -= deployment.ram
    cluster.allocated_cpu -= deployment.cpu
    cluster.allocated_gpu -= deployment.gpu

    # Mark deployment as successful
    deployment.status = "successful"

    # Commit changes to the database
    db.commit()

    # Process queued tasks
    enqueue_queued_deployments(cluster_id, db)

    return {"message": "Deployment deleted successfully and resources freed"}
