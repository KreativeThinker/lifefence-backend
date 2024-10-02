from fastapi import APIRouter

router = APIRouter(prefix="/location", tags=["location"])


@router.get("/")
async def get_location():
    return "location"
