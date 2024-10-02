from fastapi import APIRouter

router = APIRouter(prefix="/expense", tags=["expense"])


@router.get("/")
async def get_expenses():
    return "expenses"
