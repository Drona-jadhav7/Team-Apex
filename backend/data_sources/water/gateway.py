from dataclasses import dataclass, asdict
from typing import Optional
import math


@dataclass
class WaterObservation:
    latitude: float
    longitude: float

    station_name: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None

    ph: Optional[float] = None
    ec_us_cm: Optional[float] = None
    tds_mg_l: Optional[float] = None
    fluoride_mg_l: Optional[float] = None
    nitrate_mg_l: Optional[float] = None
    chloride_mg_l: Optional[float] = None
    iron_mg_l: Optional[float] = None

    observation_date: Optional[str] = None

    source: str = ""
    source_url: str = ""

    def to_dict(self):
        return asdict(self)


class WaterProviderError(Exception):
    """Base error for water-data providers."""


class WaterProviderUnavailable(WaterProviderError):
    """Provider could not be reached."""


class WaterDataGateway:

    def __init__(self):
        self.sources = []

    def add_source(self, source):
        self.sources.append(source)

    @staticmethod
    def distance_km(
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float,
    ) -> float:

        radius = 6371.0088

        p1 = math.radians(lat1)
        p2 = math.radians(lat2)

        dp = math.radians(lat2 - lat1)
        dl = math.radians(lon2 - lon1)

        a = (
            math.sin(dp / 2) ** 2
            + math.cos(p1)
            * math.cos(p2)
            * math.sin(dl / 2) ** 2
        )

        return 2 * radius * math.asin(math.sqrt(a))

    def nearby(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 25.0,
    ):

        matches = []
        provider_errors = []

        for source in self.sources:

            try:
                observations = source.get_observations(
                    latitude=latitude,
                    longitude=longitude,
                    radius_km=radius_km,
                )

                for observation in observations:

                    distance = self.distance_km(
                        latitude,
                        longitude,
                        observation.latitude,
                        observation.longitude,
                    )

                    if distance <= radius_km:
                        matches.append(
                            (observation, distance)
                        )

            except WaterProviderUnavailable as exc:
                provider_errors.append({
                    "source": getattr(
                        source,
                        "name",
                        source.__class__.__name__,
                    ),
                    "status": "provider_unavailable",
                    "message": str(exc),
                })

            except Exception as exc:
                provider_errors.append({
                    "source": getattr(
                        source,
                        "name",
                        source.__class__.__name__,
                    ),
                    "status": "error",
                    "message": str(exc),
                })

        matches.sort(key=lambda item: item[1])

        if matches:
            status = "available"
        elif provider_errors:
            status = "provider_unavailable"
        else:
            status = "no_data"

        return {
            "status": status,
            "observation_count": len(matches),
            "observations": [
                {
                    "distance_km": round(distance, 3),
                    "data": observation.to_dict(),
                }
                for observation, distance in matches
            ],
            "provider_errors": provider_errors,
        }