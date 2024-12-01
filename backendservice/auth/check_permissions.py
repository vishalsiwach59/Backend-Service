from functools import wraps
from fastapi import Depends, HTTPException, status
from backendservice.databaseModels.models import Permission

from functools import wraps
from fastapi import HTTPException, status

def check_permission(resource: str, action: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get the user and db from the dependencies passed by FastAPI
            user = kwargs.get("user")
            if not user:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not authenticated")
            
            db = kwargs.get("db")
            # Check for permission in the database
            permission = db.query(Permission).filter(
                Permission.role == user.role,
                Permission.resource == resource,
                Permission.action == action
            ).first()
            if not permission:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
            
            # Call the original function if permissions are granted
            return await func(*args, **kwargs)
        return wrapper
    return decorator

