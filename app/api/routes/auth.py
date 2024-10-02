from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, field_validator

from app.models.user import User, User_Pydantic
from app.utils.auth import (
    create_access_token,
    decode_token,
    get_password_hash,
    security,
    verify_password,
)

router = APIRouter()


class Token(BaseModel):
    access_token: str
    token_type: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserSignup(BaseModel):
    username: str
    name: str
    email: EmailStr
    password: str
    dob: date

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v):
        if not v.isalnum():
            raise ValueError("Username must be alphanumeric")
        return v

    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

    # TODO: add field_validator for dob


@router.post("/signup", response_model=User_Pydantic)
async def signup(user: UserSignup):
    # Check if username already exists
    if await User.exists(username=user.username):
        raise HTTPException(status_code=400, detail="Username already registered")

    # Check if email already exists
    if await User.exists(email=user.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create new user
    hashed_password = get_password_hash(user.password)

    user_obj = await User.create(
        username=user.username,
        name=user.name,
        email=user.email,
        password=hashed_password,
        dob=user.dob,
    )

    return await User_Pydantic.from_tortoise_orm(user_obj)


@router.post("/login", response_model=Token)
async def login(user_login: UserLogin):
    user = await User.get_or_none(username=user_login.username)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    if not verify_password(user_login.password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    # Create access token
    access_token = create_access_token(data={"sub": user.username})

    return Token(access_token=access_token, token_type="bearer")


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


@router.get("/me", response_model=User_Pydantic)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return await User_Pydantic.from_tortoise_orm(current_user)
