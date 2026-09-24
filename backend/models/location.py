from pydantic import BaseModel, Field
from typing import Optional


class Location(BaseModel):
    name: str
    city: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    country_code: Optional[str] = None

    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)

    postcode: Optional[str] = None
    display_name: Optional[str] = None

    source: str = "nominatim"


class LocationSearchResponse(BaseModel):
    success: bool
    location: Optional[Location] = None
    message: Optional[str] = None