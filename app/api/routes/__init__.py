from fastapi import APIRouter

from app.api.routes import auth, expense, group, location, task, user

router = APIRouter(prefix="/api")

router.include_router(auth.router)
router.include_router(expense.router)
router.include_router(group.router)
router.include_router(location.router)
router.include_router(task.router)
router.include_router(user.router)
