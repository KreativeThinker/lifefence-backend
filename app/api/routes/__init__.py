from fastapi import APIRouter

from app.api.routes import auth, expense, group, location, todo, user

router = APIRouter(prefix="/api")

router.include_router(auth.router)
router.include_router(expense.router)
router.include_router(group.router)
router.include_router(location.router)
router.include_router(todo.router)
router.include_router(user.router)
