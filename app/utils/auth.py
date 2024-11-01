from datetime import UTC, datetime, timedelta
from typing import Optional

from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.models.user import User

security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

from app.config import config


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(hours=config.jwt_valid_duration)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, config.jwt_secret, algorithm=config.encoding_algorithm
    )
    return encoded_jwt


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token, config.jwt_secret, algorithms=[config.encoding_algorithm]
        )
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> User:
    try:
        token = credentials.credentials
        payload = decode_token(token)
        username = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=401, detail="Could not validate credentials"
            )
    except Exception:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    user = await User.get_or_none(username=username)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user
