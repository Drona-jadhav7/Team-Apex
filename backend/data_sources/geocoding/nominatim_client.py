from typing import Any
import time

import requests


class NominatimClient:
    """
    Client for the public OpenStreetMap Nominatim geocoding API.

    Nominatim usage policy:
    - Maximum 1 request per second
    - Identify the application with a custom User-Agent
    - Cache/reuse results where possible
    """

    BASE_URL = "https://nominatim.openstreetmap.org"

    def __init__(
        self,
        user_agent: str = "IndiaAIGrid/0.1",
        timeout: int = 10,
    ):
        self.timeout = timeout
        self.session = requests.Session()

        self.session.headers.update(
            {
                "User-Agent": user_agent,
                "Accept": "application/json",
            }
        )

        self._last_request_time = 0.0

    def _respect_rate_limit(self) -> None:
        """
        Ensure we do not exceed Nominatim's public API rate limit.
        """
        elapsed = time.monotonic() - self._last_request_time

        if elapsed < 1.0:
            time.sleep(1.0 - elapsed)

    def _get(self, endpoint: str, params: dict[str, Any]) -> Any:
        self._respect_rate_limit()

        response = self.session.get(
            f"{self.BASE_URL}{endpoint}",
            params=params,
            timeout=self.timeout,
        )

        self._last_request_time = time.monotonic()

        response.raise_for_status()

        return response.json()

    def search(self, query: str, limit: int = 1) -> list[dict[str, Any]]:
        """
        Forward geocoding.

        Example:
            search("Nashik, Maharashtra, India")
        """

        if not query or not query.strip():
            raise ValueError("Location query cannot be empty.")

        params = {
            "q": query.strip(),
            "format": "jsonv2",
            "addressdetails": 1,
            "limit": min(limit, 5),
            "countrycodes": "in",
        }

        return self._get("/search", params)

    def reverse(
        self,
        latitude: float,
        longitude: float,
    ) -> dict[str, Any]:
        """
        Reverse geocoding.

        Converts coordinates into an address.
        """

        params = {
            "lat": latitude,
            "lon": longitude,
            "format": "jsonv2",
            "addressdetails": 1,
        }

        return self._get("/reverse", params)