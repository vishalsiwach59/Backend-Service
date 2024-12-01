import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from backendservice.auth.auth import (
    hash_password,
    verify_password,
    create_access_token,
    verify_jwt,
    get_current_user,
)
from backendservice.databaseModels.models import User
from backendservice.databaseModels.database import SessionLocal
from datetime import timedelta

# Mock data and utilities
TEST_SECRET_KEY = "testsecretkey"
TEST_USER_ID = 123
TEST_PASSWORD = "securepassword"
TEST_HASHED_PASSWORD = hash_password(TEST_PASSWORD)
TEST_TOKEN = create_access_token({"sub": str(TEST_USER_ID)})

# Mock database session and models
@pytest.fixture
def db_session():
    session = SessionLocal()
    yield session
    session.close()

@pytest.fixture
def test_user(db_session):
    user = User(id=TEST_USER_ID, username="testuser", hashed_password=TEST_HASHED_PASSWORD)
    db_session.add(user)
    db_session.commit()
    return user

def test_hash_password():
    hashed = hash_password(TEST_PASSWORD)
    assert hashed != TEST_PASSWORD
    assert len(hashed) > 0

def test_verify_password():
    assert verify_password(TEST_PASSWORD, TEST_HASHED_PASSWORD)
    assert not verify_password("wrongpassword", TEST_HASHED_PASSWORD)

def test_create_access_token():
    token = create_access_token({"sub": str(TEST_USER_ID)})
    assert token is not None
    assert len(token) > 0

def test_verify_jwt_valid_token():
    payload = verify_jwt(TEST_TOKEN)
    assert payload["sub"] == str(TEST_USER_ID)

def test_verify_jwt_invalid_token():
    with pytest.raises(Exception):  # JWT decode should fail
        verify_jwt("invalidtoken")

def test_get_current_user_invalid_token(db_session):
    with pytest.raises(Exception):  # Should raise an HTTPException
        get_current_user(token="invalidtoken", db=db_session)

def test_get_current_user_user_not_found(db_session):
    # Token for non-existent user
    token = create_access_token({"sub": "nonexistent"})
    with pytest.raises(Exception):  # Should raise an HTTPException
        get_current_user(token=token, db=db_session)
