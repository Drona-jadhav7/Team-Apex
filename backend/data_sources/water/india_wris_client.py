import requests

from backend.data_sources.water.gateway import (
    WaterProviderUnavailable,
)


class IndiaWRISClient:

    name = "india_wris"

    BASE_URL = "https://indiawris.gov.in"

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

        self.session = requests.Session()

        self.session.headers.update({
            "User-Agent": "IndiaAIGrid/0.1",
            "Accept": "application/json",
        })

    def _request(self, endpoint: str, params=None):

        try:
            response = self.session.get(
                f"{self.BASE_URL}{endpoint}",
                params=params,
                timeout=self.timeout,
            )

        except requests.RequestException as exc:
            raise WaterProviderUnavailable(
                f"India-WRIS is currently unreachable: {exc}"
            ) from exc

        if response.status_code >= 500:
            raise WaterProviderUnavailable(
                f"India-WRIS returned HTTP {response.status_code}"
            )

        if response.status_code >= 400:
            raise WaterProviderUnavailable(
                f"India-WRIS request failed with HTTP "
                f"{response.status_code}"
            )

        return response.json()

    def get_observations(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 25.0,
    ):
        """
        India-WRIS integration point.

        The public API endpoint is known from official
        government documentation, but the exact live
        request schema still needs to be confirmed.

        Do not fabricate observations here.
        """

        raise WaterProviderUnavailable(
            "India-WRIS groundwater-quality request schema "
            "has not yet been configured."
        )