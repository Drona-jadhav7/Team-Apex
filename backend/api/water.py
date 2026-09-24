from fastapi import APIRouter, Query

from backend.data_sources.water.gateway import (
    WaterDataGateway,
)
from backend.data_sources.water.india_wris_client import (
    IndiaWRISClient,
)
from backend.services.water_data_service import (
    WaterDataService,
)


router = APIRouter(
    prefix="/api/water",
    tags=["Water"],
)


gateway = WaterDataGateway()

gateway.add_source(
    IndiaWRISClient()
)

service = WaterDataService(
    gateway=gateway,
)


@router.get("/nearby")
def nearby_water(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(
        25.0,
        gt=0,
        le=100,
    ),
):

    return service.get_nearby_water_data(
        latitude=lat,
        longitude=lon,
        radius_km=radius_km,
    )