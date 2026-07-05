"""
Authentication Router - Simple single-role login (MVP scope)
"""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer
from pydantic import BaseModel
import os
import logging
from datetime import datetime, timedelta
from jose import JWTError, jwt

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

# Security config
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 24 * 60  # 24 hours
security = HTTPBearer()

# Simple hardcoded credentials (MVP scope)
# In production, this would be in a database
VALID_USERNAME = os.getenv("SALES_USERNAME", "sales")
VALID_PASSWORD = os.getenv("SALES_PASSWORD", "sales123")


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


class TokenData(BaseModel):
    username: str
    expires: datetime


def create_access_token(username: str) -> str:
    """Create JWT access token."""
    expires = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": username,
        "exp": expires
    }
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(credentials = Depends(security)) -> str:
    """Validate and extract username from JWT token."""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Login endpoint - returns JWT token.
    MVP: Single hardcoded user.
    """
    if request.username != VALID_USERNAME or request.password != VALID_PASSWORD:
        logger.warning(f"Failed login attempt for user: {request.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    token = create_access_token(request.username)
    logger.info(f"Successful login for user: {request.username}")
    
    return LoginResponse(
        access_token=token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60  # in seconds
    )


@router.get("/verify")
async def verify_token(current_user: str = Depends(get_current_user)):
    """Verify if the current token is valid."""
    return {"username": current_user, "status": "authenticated"}
