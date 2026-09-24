from fastapi import APIRouter, HTTPException, Query

from backend.models.location import LocationSearchResponse
from backend.services.location_service import LocationService


router = APIRouter(
    prefix="/api/location",
    tags=["Location"],
)

location_service = LocationService()


@router.get(
    "/search",
    response_model=LocationSearchResponse,
)
def search_location(
    q: str = Query(
        ...,
        min_length=2,
        description="Location name or address",
    )
):
    location = location_service.search(q)

    if location is None:
        raise HTTPException(
            status_code=404,
            detail=f"Location not found: {q}",
        )

    return LocationSearchResponse(
        success=True,
        location=location,
    )


@router.get(
    "/reverse",
    response_model=LocationSearchResponse,
)
def reverse_location(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
):
    location = location_service.reverse(lat, lon)

    return LocationSearchResponse(
        success=True,
        location=location,
    )