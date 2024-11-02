from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from tortoise.transactions import atomic

from app.models.location import (
    Blacklist,
    Location,
    Location_Pydantic,
    Office,
    Residence,
)
from app.models.user import User
from app.utils.auth import get_current_user

router = APIRouter(prefix="/location", tags=["location"])


class LocationInput(BaseModel):
    address: str
    latitude: float
    longitude: float
    location_type: str


@router.get("/view/all")
async def view_all_addresses(current_user: User = Depends(get_current_user)):
    locations = await Location_Pydantic.from_queryset(
        Location.filter(user=current_user)
    )
    return locations


@router.get("/view/residence")
async def view_residence(current_user: User = Depends(get_current_user)):
    residence = await Location.get_or_none(residence_location__user=current_user)
    if not residence:
        raise HTTPException(status_code=404, detail="Residence not assigned")

    return await Location_Pydantic.from_tortoise_orm(residence)


@router.get("/view/office")
async def view_office(current_user: User = Depends(get_current_user)):
    office = await Location.get_or_none(office_location__user=current_user)
    if not office:
        raise HTTPException(status_code=404, detail="Residence not assigned")

    return await Location_Pydantic.from_tortoise_orm(office)


@router.get("/view/blacklist")
async def view_blacklist(current_user: User = Depends(get_current_user)):
    blacklisted = await Location_Pydantic.from_queryset(
        Location.filter(blacklisted_location__user=current_user)
    )
    return blacklisted


@atomic()
@router.post("/set/residence", response_model=Location_Pydantic)
async def set_residence(
    location_id: int, current_user: User = Depends(get_current_user)
):
    location = await Location.get_or_none(id=location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    # Check if already a residence
    existing = await Residence.get_or_none(location=location, user=current_user)
    if existing:
        raise HTTPException(status_code=400, detail="Already set as residence")

    await Residence.create(location=location, user=current_user)
    return await Location_Pydantic.from_tortoise_orm(location)


@atomic()
@router.post("/set/office", response_model=Location_Pydantic)
async def set_office(location_id: int, current_user: User = Depends(get_current_user)):
    location = await Location.get_or_none(id=location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    # Check if already an office
    existing = await Office.get_or_none(location=location, user=current_user)
    if existing:
        raise HTTPException(status_code=400, detail="Already set as office")

    await Office.create(location=location, user=current_user)
    return await Location_Pydantic.from_tortoise_orm(location)


@atomic()
@router.post("/blacklist", response_model=Location_Pydantic)
async def blacklist_location(
    location_id: int, current_user: User = Depends(get_current_user)
):
    location = await Location.get_or_none(id=location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    # Check if already blacklisted
    existing = await Blacklist.get_or_none(location=location, user=current_user)
    if existing:
        raise HTTPException(status_code=400, detail="Location already blacklisted")

    await Blacklist.create(location=location, user=current_user)
    return await Location_Pydantic.from_tortoise_orm(location)


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
    return location
