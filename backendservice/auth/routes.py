from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from backendservice.databaseModels import database, models
from typing import List
from fastapi import HTTPException, Depends
from backendservice.auth.auth import hash_password, create_access_token, verify_password, get_current_user
from backendservice.databaseModels import models
from backendservice.databaseModels.schemas import *

router = APIRouter()

@router.post("/register")
def register_user(user: UserCreate, db: Session = Depends(database.get_db)):
    existing_user = db.query(models.User).filter(models.User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Create the user
    hashed_password = hash_password(user.password)
    print(hashed_password)
    new_user = models.User(username=user.username, password_hash=hashed_password, role="admin")  # Default role is 'viewer'
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully"}

@router.post("/login")
def login_user(credentials: Login, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.username == credentials.username).first()
    print(f"crentail 1st {credentials.password} user hash {user.password_hash}")
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Create JWT token
    print(f"user id is {user.id}")
    access_token = create_access_token(data={"sub": user.id})
    return {"access_token": access_token, "token_type": "bearer"}
