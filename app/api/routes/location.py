# from fastapi import APIRouter, Depends
# from pydantic import BaseModel
# from tortoise.transactions import atomic
#
# from app.api.routes.auth import get_current_user
# from app.models.location import Location
# from app.models.user import User
#
# router = APIRouter(prefix="/location", tags=["location"])
#
#
# class LocationInput(BaseModel):
#     address: str
#     latitude: float
#     longitude: float
#     location_type: str
#
#
# @router.get("/")
# async def get_location():
#     return "location"
#
#
# @atomic()
# @router.post("/new")
# async def new_location(
#     new_location: LocationInput,
#     current_user: User = Depends(get_current_user),
# ): ...
#
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from tortoise.transactions import atomic

from app.api.routes.auth import get_current_user
from app.models.location import Location, Location_Pydantic
from app.models.user import User

router = APIRouter(prefix="/location", tags=["location"])


class LocationInput(BaseModel):
    address: str
    latitude: float
    longitude: float
    location_type: str
    address_type: str


@router.get("/")
async def get_location():
    return "location"


@router.get("/view/all")
async def view_all_addresses(current_user: User = Depends(get_current_user)):
    pass


@router.get("/view/residence")
async def view_residence(current_user: User = Depends(get_current_user)):
    pass


@router.get("/view/office")
async def view_office(current_user: User = Depends(get_current_user)):
    pass


@router.get("/view/blacklist")
async def view_blacklist(current_user: User = Depends(get_current_user)):
    pass


@router.post("/set/residence")
async def set_residence(
    location: Location, current_user: User = Depends(get_current_user)
):
    pass


@router.post("/set/office")
async def set_office(
    location: Location, current_user: User = Depends(get_current_user)
):
    pass


@router.post("/blacklist")
async def blacklist_location(
    location: Location, current_user: User = Depends(get_current_user)
):
    pass


@router.post("/new", response_model=Location_Pydantic)
async def create_new_address(
    location_data: LocationInput,
    current_user: User = Depends(get_current_user),
):
    location = await Location.create(
        address=location_data.address,
        latitude=location_data.latitude,
        longitude=location_data.longitude,
        location_type=location_data.location_type,
        user=current_user,
    )
    return await Location_Pydantic.from_tortoise_orm(location)
