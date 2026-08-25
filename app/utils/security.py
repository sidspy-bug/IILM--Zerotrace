"""
Security utilities — JWT, password hashing, RBAC.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os
import logging
import secrets

from app.database.database import get_db
from app.models.user import User

# Configuration
# SECRET_KEY: prefer env-provided secret. If not present and DEV_MODE is enabled,
# generate a secure random secret for local development and log a warning.
SECRET_KEY = os.getenv("SECRET_KEY")
DEV_MODE = os.getenv("DEV_MODE", "0").lower() in ("1", "true", "yes")
if not SECRET_KEY:
    if DEV_MODE:
        # Generate a secure random key for local development only
        SECRET_KEY = secrets.token_urlsafe(48)
        logging.warning(
            "DEV_MODE is enabled and no SECRET_KEY was provided — a runtime-only secret was generated. "
            "Do NOT use this in production. Set the SECRET_KEY environment variable for real deployments."
        )
    else:
        raise RuntimeError(
            "SECRET_KEY environment variable must be set. Do NOT run the application with a hard-coded default secret. "
            "To allow a development fallback, set DEV_MODE=1 (not for production)."
        )

ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Valid roles
VALID_ROLES = ["ADMIN", "INVESTIGATOR", "FORENSIC_EXAMINER", "VIEWER"]

# Role hierarchy for access control
ROLE_HIERARCHY = {
    "ADMIN": 4,
    "INVESTIGATOR": 3,
    "FORENSIC_EXAMINER": 2,
    "VIEWER": 1,
}


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Decode JWT token and return the current user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user


def require_role(*allowed_roles: str):
    """Dependency factory to restrict access by role."""
    async def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role(s): {', '.join(allowed_roles)}",
            )
        return current_user
    return role_checker
