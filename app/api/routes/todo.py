from fastapi import APIRouter

router = APIRouter(prefix="/todo", tags=["todo"])


@router.get("/")
async def get_todo():
    return "todo"
