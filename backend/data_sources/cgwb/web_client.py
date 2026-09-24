from typing import Optional
import requests


class CGWBWebClient:

    def __init__(
        self,
        timeout: int = 20,
        user_agent: str = "IndiaAIGrid/0.1",
    ):
        self.timeout = timeout

        self.session = requests.Session()

        self.session.headers.update(
            {
                "User-Agent": user_agent,
                "Accept": "*/*",
            }
        )

    def fetch_document(
        self,
        url: str,
    ) -> bytes:

        response = self.session.get(
            url,
            timeout=self.timeout,
        )

        response.raise_for_status()

        return response.content