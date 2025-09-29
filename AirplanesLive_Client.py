"""Simple httpx-based client for the Airplanes.live REST API.

This module provides a small synchronous client that respects the documented
rate limit (1 request per second) and does simple retries with exponential
backoff for transient errors.

Usage:
    from airplanes_client import AirplanesClient

    c = AirplanesClient()
    data = c.get_icao('45211e')

"""
from __future__ import annotations

import time
import logging
from typing import Any, Dict, Iterable, List, Optional, Sequence, Mapping

import httpx

logger = logging.getLogger(__name__)



class AirplanesClient:
    """Sync client for the Airplanes.live API using httpx.Client.

    Behavior / contract:
    - Inputs: endpoint parameters as strings / numeric values
    - Output: parsed JSON (Python objects) returned from the API on success
    - Errors: Raises httpx.RequestError or RuntimeError on repeated failures

    Notes:
    - The public API is intentionally small and maps directly to documented
      endpoints (icao, hex, callsign, reg, type, point, etc.).
    - The API is rate limited to 1 request/sec; the client enforces a default
      1.0s delay between requests.
    """

    def __init__(
        self,
        base_url: str = "https://api.airplanes.live/v2",
        timeout: float = 10.0,
        rate_limit_seconds: float = 2.0,
        max_retries: int = 3,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.client: httpx.Client = httpx.Client(base_url=self.base_url, timeout=timeout)
        self.rate_limit_seconds: float = float(rate_limit_seconds)
        self.max_retries: int = int(max_retries)
        self._last_request_ts: float = 0.0

    def close(self) -> None:
        try:
            self.client.close()
        except Exception:
            pass

    def _throttle(self) -> None:
        """Ensure at least `rate_limit_seconds` between requests."""
        now = time.time()
        elapsed = now - self._last_request_ts
        wait = self.rate_limit_seconds - elapsed
        if wait > 0:
            logger.debug("Throttling for %.3fs to respect rate limit", wait)
            time.sleep(wait)

    def _request(self, path: str, params: Optional[Mapping[str, Any]] = None) -> Any:
        """Perform a GET request to an API path (path is relative to base_url).

        Retries on network errors and 5xx responses with exponential backoff.
        """
        attempt = 0
        while True:
            attempt += 1
            self._throttle()
            try:
                resp: httpx.Response = self.client.get(path, params=params)
                #print(resp.url)
                self._last_request_ts = time.time()
                resp.raise_for_status()
                return resp.json()
            except httpx.HTTPStatusError as e:
                status = e.response.status_code
                logger.warning(
                    "HTTP error on request %s (status=%s): %s",
                    path,
                    status,
                    e,
                )
                # 429 or 5xx -> retry (up to max_retries), others -> raise
                if status == 429 or 500 <= status < 600:
                    if attempt >= self.max_retries:
                        raise
                    backoff = 2 ** attempt
                    logger.info("Sleeping %.1fs before retrying (attempt %d)", backoff, attempt)
                    time.sleep(backoff)
                    continue
                raise
            except httpx.RequestError as e:
                logger.warning("Request error on %s: %s", path, e)
                if attempt >= self.max_retries:
                    raise
                backoff = 2 ** attempt
                logger.info("Sleeping %.1fs before retrying (attempt %d)", backoff, attempt)
                time.sleep(backoff)
                continue

    # --- Endpoint helpers ---
    def get_icao(self, icao: str) -> Any:
        """GET /icao/[icao]"""
        icao = str(icao).strip()
        return self._request(f"/icao/{icao}")

    def get_hex(self, hex_ids: Sequence[str]) -> Any:
        """GET /hex/[hex] - accepts comma-separated ids or iterable"""
        val = ",".join(str(h).strip() for h in hex_ids)
        return self._request(f"/hex/{val}")

    def get_callsign(self, callsign: str) -> Any:
        """GET /callsign/[callsign]"""
        return self._request(f"/callsign/{str(callsign).strip()}")

    def get_reg(self, regs: Sequence[str]) -> Any:
        """GET /reg/[reg] - accepts comma-separated list"""
        val = ",".join(str(r).strip() for r in regs)
        return self._request(f"/reg/{val}")

    def get_type(self, types: Sequence[str]) -> Any:
        """GET /type/[type] - accepts comma-separated ICAO type codes"""
        val = ",".join(str(t).strip() for t in types)
        return self._request(f"/type/{val}")

    def get_squawk(self, squawk: str) -> Any:
        return self._request(f"/squawk/{str(squawk).strip()}")

    def get_mil(self) -> Any:
        return self._request("/mil")

    def get_ladd(self) -> Any:
        return self._request("/ladd")

    def get_pia(self) -> Any:
        return self._request("/pia")

    def get_point(self, lat: float, lon: float, radius_nm: float) -> List[Dict[str, Any]] | None:
        """GET /point/[lat]/[lon]/[radius]

        radius is in nautical miles (the API allows up to 250 nm).
        """
        if not (-90.0 <= lat <= 90.0):
            raise ValueError("Latitude must be between -90 and 90")
        
        if not (-180.0 <= lon <= 180.0):
            raise ValueError("Longitude must be between -180 and 180")
        
        if radius_nm <= 0 or radius_nm > 250:
            raise ValueError("Radius must be between 0 and 250 nautical miles")
        
        data = self._request(f"/point/{lat}/{lon}/{radius_nm}")
        if data:
            return data.get('ac',[])

    def __enter__(self) -> "AirplanesClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
