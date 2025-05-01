from datetime import datetime, timedelta, UTC
from jose import jwt
from app.config import settings
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from app.config import settings

from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/verify-otp")

JWT_EXPIRE_MINUTES=1440

async def get_current_user(token: str = Depends(OAuth2PasswordBearer(tokenUrl="/auth/verify-otp"))) -> str:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    return email


def create_access_token(email: str) -> str:
    expire = datetime.now(UTC) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    payload = {"sub": email, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)