import os
import time

import requests


class CubeError(RuntimeError):
    pass


class CubeClient:
    """Minimal client for the Cube REST API."""

    def __init__(self, url=None, token=None):
        self.url = (url or os.environ["CUBE_API_URL"]).rstrip("/")
        self.token = token or os.environ["CUBE_API_TOKEN"]

    def load(self, query, retries=10):
        for _ in range(retries):
            resp = requests.post(
                f"{self.url}/cubejs-api/v1/load",
                json={"query": query},
                headers={"Authorization": self.token},
                timeout=60,
            )
            body = resp.json()
            if body.get("error") == "Continue wait":
                time.sleep(2)
                continue
            if resp.status_code != 200:
                raise CubeError(body.get("error", resp.text))
            return body["data"]
        raise CubeError("Cube query did not finish in time")
