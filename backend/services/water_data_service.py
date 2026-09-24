from backend.data_sources.water.gateway import (
    WaterDataGateway,
)


class WaterDataService:

    def __init__(
        self,
        gateway: WaterDataGateway,
    ):
        self.gateway = gateway

    def get_nearby_water_data(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 25.0,
    ):

        result = self.gateway.nearby(
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km,
        )

        return {
            "latitude": latitude,
            "longitude": longitude,
            "radius_km": radius_km,
            **result,
        }