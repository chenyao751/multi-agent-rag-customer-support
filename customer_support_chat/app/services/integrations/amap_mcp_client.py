"""AMap (高德地图) REST API Client

Direct REST API calls to AMap services.
"""

import requests
import json
from typing import Dict, Any, Optional
from customer_support_chat.app.core.logger import logger
from customer_support_chat.app.core.settings import get_settings

settings = get_settings()


class AMapMCPClient:
    """Client for AMap REST API services."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.AMAP_API_KEY
        self.base_url = "https://restapi.amap.com"
        self.timeout = 10

        if not self.api_key:
            logger.warning("AMap API Key not configured")

    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make a REST API request to AMap service.

        Args:
            endpoint: API endpoint (e.g., "/v3/place/text", "/v3/direction/walking")
            params: Query parameters

        Returns:
            The JSON response

        Raises:
            Exception: If the request fails
        """
        # Add API key to params
        params["key"] = self.api_key

        url = f"{self.base_url}{endpoint}"

        try:
            logger.debug(f"AMap API request: {endpoint} with params: {params}")

            response = requests.get(
                url,
                params=params,
                timeout=self.timeout
            )

            response.raise_for_status()
            result = response.json()

            logger.debug(f"AMap API response status: {result.get('status')}")

            # Check AMap API status
            if result.get("status") != "1":
                error_msg = f"AMap API Error: {result.get('info', 'Unknown error')}"
                logger.error(error_msg)
                raise Exception(error_msg)

            return result

        except requests.exceptions.Timeout:
            logger.error(f"AMap API request timed out after {self.timeout}s")
            raise Exception(f"AMap API request timed out after {self.timeout} seconds")

        except requests.exceptions.RequestException as e:
            logger.error(f"AMap API request failed: {e}")
            raise Exception(f"Failed to connect to AMap API service: {str(e)}")

        except Exception as e:
            logger.error(f"AMap API error: {e}")
            raise

    def geocode(self, address: str, city: Optional[str] = None) -> Dict[str, Any]:
        """Convert address to coordinates."""
        params = {"address": address}
        if city:
            params["city"] = city
        return self._make_request("/v3/geocode/geo", params)

    def reverse_geocode(self, location: str) -> Dict[str, Any]:
        """Convert coordinates to address."""
        params = {"location": location}
        return self._make_request("/v3/geocode/regeo", params)

    def search_place(self, keywords: str, city: Optional[str] = None) -> Dict[str, Any]:
        """Search places by keyword."""
        params = {"keywords": keywords}
        if city:
            params["city"] = city
        return self._make_request("/v3/place/text", params)

    def search_around(self, keywords: str, location: str, radius: Optional[int] = None) -> Dict[str, Any]:
        """Search nearby places."""
        params = {
            "keywords": keywords,
            "location": location
        }
        if radius:
            params["radius"] = radius
        return self._make_request("/v3/place/around", params)

    def get_place_detail(self, poi_id: str) -> Dict[str, Any]:
        """Get place detail by ID."""
        params = {"id": poi_id}
        return self._make_request("/v3/place/detail", params)

    def plan_walking(self, origin: str, destination: str) -> Dict[str, Any]:
        """Plan walking route."""
        params = {
            "origin": origin,
            "destination": destination
        }
        return self._make_request("/v3/direction/walking", params)

    def plan_bicycling(self, origin: str, destination: str) -> Dict[str, Any]:
        """Plan bicycling route."""
        params = {
            "origin": origin,
            "destination": destination
        }
        return self._make_request("/v4/direction/bicycling", params)

    def plan_driving(self, origin: str, destination: str) -> Dict[str, Any]:
        """Plan driving route."""
        params = {
            "origin": origin,
            "destination": destination
        }
        return self._make_request("/v3/direction/driving", params)

    def plan_transit(self, origin: str, destination: str, city: str, cityd: Optional[str] = None) -> Dict[str, Any]:
        """Plan public transit route."""
        params = {
            "origin": origin,
            "destination": destination,
            "city": city
        }
        if cityd:
            params["cityd"] = cityd
        return self._make_request("/v3/direction/transit/integrated", params)

    def measure_distance(self, origins: str, destination: str) -> Dict[str, Any]:
        """Measure distance between points."""
        params = {
            "origins": origins,
            "destination": destination,
            "type": "1"  # 1=直线距离, 0=驾车导航距离
        }
        return self._make_request("/v3/distance", params)


# Singleton instance
_amap_client_instance = None


def get_amap_client() -> AMapMCPClient:
    """Get the singleton AMap client instance."""
    global _amap_client_instance
    if _amap_client_instance is None:
        _amap_client_instance = AMapMCPClient()
    return _amap_client_instance
