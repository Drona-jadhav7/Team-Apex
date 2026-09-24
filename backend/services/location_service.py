from typing import Any

from backend.data_sources.geocoding.nominatim_client import NominatimClient
from backend.models.location import Location


class LocationService:
    """
    Application-level location service.

    External API details stay inside NominatimClient.
    """

    def __init__(self, geocoder: NominatimClient | None = None):
        self.geocoder = geocoder or NominatimClient()

    def _normalize(self, result: dict[str, Any]) -> Location:
        address = result.get("address", {})

        city = (
            address.get("city")
            or address.get("town")
            or address.get("municipality")
            or address.get("village")
        )

        district = (
            address.get("county")
            or address.get("state_district")
        )

        return Location(
            name=city or result.get("name") or result.get("display_name", ""),
            city=city,
            district=district,
            state=address.get("state"),
            country=address.get("country"),
            country_code=address.get("country_code"),
            latitude=float(result["lat"]),
            longitude=float(result["lon"]),
            postcode=address.get("postcode"),
            display_name=result.get("display_name"),
            source="nominatim",
        )

    def search(self, query: str) -> Location | None:
        results = self.geocoder.search(query)

        if not results:
            return None

        return self._normalize(results[0])

    def reverse(
        self,
        latitude: float,
        longitude: float,
    ) -> Location:
        result = self.geocoder.reverse(latitude, longitude)

        return self._normalize(result)