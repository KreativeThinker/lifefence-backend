from fastapi import APIRouter, Depends

from app.api.routes.auth import get_current_user
from app.models.user import User, User_Pydantic

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/me", response_model=User_Pydantic)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return await User_Pydantic.from_tortoise_orm(current_user)
