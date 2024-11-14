from fastapi import APIRouter

from app.api.routes import (
    actions,
    auth,
    expense,
    group,
    group_task,
    location,
    task,
    user,
)

router = APIRouter(prefix="/api")

router.include_router(auth.router)
router.include_router(expense.router)
router.include_router(group.router)
router.include_router(location.router)
router.include_router(task.router)
router.include_router(user.router)
router.include_router(group_task.router)
router.include_router(actions.router)
