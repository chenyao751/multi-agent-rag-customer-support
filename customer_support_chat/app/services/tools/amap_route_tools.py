"""AMap (高德地图) MCP Tools

LangChain tool wrappers for AMap MCP service.
Focus on route planning and navigation services.
"""

import json
from typing import Optional
from langchain_core.tools import tool
from customer_support_chat.app.core.logger import logger
from customer_support_chat.app.services.integrations.amap_mcp_client import get_amap_client


@tool
def geocode_address(address: str, city: Optional[str] = None) -> str:
    """Convert a detailed address to GPS coordinates (latitude and longitude).

    Args:
        address: Detailed address (e.g., '北京市朝阳区阜通东大街6号')
        city: City name (optional, helps with accuracy)

    Returns:
        JSON string containing location coordinates
    """
    try:
        logger.info(f"🗺️ Geocoding address: {address}")

        client = get_amap_client()
        result = client.geocode(address, city)

        logger.info(f"🗺️ Geocoded: {address}")

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        error_msg = f"Failed to geocode address: {str(e)}"
        logger.error(f"❌ {error_msg}")

        return json.dumps({
            "error": error_msg,
            "address": address
        }, ensure_ascii=False)


@tool
def reverse_geocode(location: str) -> str:
    """Convert GPS coordinates to detailed address information.

    Args:
        location: GPS coordinates in format 'longitude,latitude' (e.g., '116.481488,39.990464')

    Returns:
        JSON string containing address components (province, city, district, etc.)
    """
    try:
        logger.info(f"🗺️ Reverse geocoding: {location}")

        client = get_amap_client()
        result = client.reverse_geocode(location)

        logger.info(f"🗺️ Reverse geocoded: {location}")

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        error_msg = f"Failed to reverse geocode: {str(e)}"
        logger.error(f"❌ {error_msg}")

        return json.dumps({
            "error": error_msg,
            "location": location
        }, ensure_ascii=False)


@tool
def plan_walking_route(origin: str, destination: str) -> str:
    """Plan a walking route between two locations (up to 100km).

    Args:
        origin: Origin coordinates 'longitude,latitude' (e.g., '116.481028,39.989643')
        destination: Destination coordinates 'longitude,latitude'

    Returns:
        JSON string containing route details (distance, duration, steps)
    """
    try:
        logger.info(f"🚶 Planning walking route: {origin} → {destination}")

        client = get_amap_client()
        result = client.plan_walking(origin, destination)

        logger.info(f"🚶 Walking route planned")

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        error_msg = f"Failed to plan walking route: {str(e)}"
        logger.error(f"❌ {error_msg}")

        return json.dumps({
            "error": error_msg,
            "origin": origin,
            "destination": destination
        }, ensure_ascii=False)


@tool
def plan_bicycling_route(origin: str, destination: str) -> str:
    """Plan a bicycling route between two locations (up to 500km).

    Considers factors like overpasses, one-way streets, and road closures.

    Args:
        origin: Origin coordinates 'longitude,latitude' (e.g., '116.481028,39.989643')
        destination: Destination coordinates 'longitude,latitude'

    Returns:
        JSON string containing route details (distance, duration, steps)
    """
    try:
        logger.info(f"🚴 Planning bicycling route: {origin} → {destination}")

        client = get_amap_client()
        result = client.plan_bicycling(origin, destination)

        logger.info(f"🚴 Bicycling route planned")

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        error_msg = f"Failed to plan bicycling route: {str(e)}"
        logger.error(f"❌ {error_msg}")

        return json.dumps({
            "error": error_msg,
            "origin": origin,
            "destination": destination
        }, ensure_ascii=False)


@tool
def plan_driving_route(origin: str, destination: str) -> str:
    """Plan a driving route for cars between two locations.

    Args:
        origin: Origin coordinates 'longitude,latitude' (e.g., '116.481028,39.989643')
        destination: Destination coordinates 'longitude,latitude'

    Returns:
        JSON string containing route details (distance, duration, path information)
    """
    try:
        logger.info(f"🚗 Planning driving route: {origin} → {destination}")

        client = get_amap_client()
        result = client.plan_driving(origin, destination)

        logger.info(f"🚗 Driving route planned")

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        error_msg = f"Failed to plan driving route: {str(e)}"
        logger.error(f"❌ {error_msg}")

        return json.dumps({
            "error": error_msg,
            "origin": origin,
            "destination": destination
        }, ensure_ascii=False)


@tool
def plan_transit_route(
    origin: str,
    destination: str,
    city: str,
    cityd: Optional[str] = None
) -> str:
    """Plan a public transit route (bus, subway, train) between two locations.

    For cross-city travel, both origin city and destination city must be provided.

    Args:
        origin: Origin coordinates 'longitude,latitude' (e.g., '116.481028,39.989643')
        destination: Destination coordinates 'longitude,latitude'
        city: Origin city name (e.g., '北京')
        cityd: Destination city name (required for cross-city travel)

    Returns:
        JSON string containing transit route details
    """
    try:
        logger.info(f"🚇 Planning transit route: {origin} → {destination}")

        client = get_amap_client()
        result = client.plan_transit(origin, destination, city, cityd)

        logger.info(f"🚇 Transit route planned")

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        error_msg = f"Failed to plan transit route: {str(e)}"
        logger.error(f"❌ {error_msg}")

        return json.dumps({
            "error": error_msg,
            "origin": origin,
            "destination": destination
        }, ensure_ascii=False)


@tool
def measure_distance(origin: str, destination: str) -> str:
    """Measure the distance between two GPS coordinates.

    Args:
        origin: Origin coordinates 'longitude,latitude' (e.g., '116.481028,39.989643')
        destination: Destination coordinates 'longitude,latitude'

    Returns:
        JSON string containing distance and estimated duration
    """
    try:
        logger.info(f"📏 Measuring distance: {origin} → {destination}")

        client = get_amap_client()
        result = client.measure_distance(origin, destination)

        logger.info(f"📏 Distance measured")

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        error_msg = f"Failed to measure distance: {str(e)}"
        logger.error(f"❌ {error_msg}")

        return json.dumps({
            "error": error_msg,
            "origin": origin,
            "destination": destination
        }, ensure_ascii=False)


@tool
def search_place_by_keyword(keywords: str, city: Optional[str] = None) -> str:
    """Search for POI (Point of Interest) locations by keyword.

    Args:
        keywords: Search keywords (e.g., '星巴克', '北京大学', '酒店')
        city: City name to limit search (optional, e.g., '北京')

    Returns:
        JSON string containing list of matching places with details
    """
    try:
        logger.info(f"🔍 Searching places: {keywords}")

        client = get_amap_client()
        result = client.search_place(keywords, city)

        logger.info(f"🔍 Found places for: {keywords}")

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        error_msg = f"Failed to search places: {str(e)}"
        logger.error(f"❌ {error_msg}")

        return json.dumps({
            "error": error_msg,
            "keywords": keywords
        }, ensure_ascii=False)


@tool
def search_nearby_places(
    keywords: str,
    location: str,
    radius: Optional[int] = None
) -> str:
    """Search for nearby POI locations around a specific coordinate.

    Args:
        keywords: Search keywords (e.g., '餐厅', '地铁站', '银行')
        location: Center point coordinates 'longitude,latitude' (e.g., '116.481028,39.989643')
        radius: Search radius in meters (optional, default 1000m)

    Returns:
        JSON string containing list of nearby places
    """
    try:
        logger.info(f"🔍 Searching nearby: {keywords} near {location}")

        client = get_amap_client()
        result = client.search_around(keywords, location, radius)

        logger.info(f"🔍 Found nearby places")

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        error_msg = f"Failed to search nearby places: {str(e)}"
        logger.error(f"❌ {error_msg}")

        return json.dumps({
            "error": error_msg,
            "keywords": keywords,
            "location": location
        }, ensure_ascii=False)


@tool
def get_place_detail(poi_id: str) -> str:
    """Get detailed information about a specific POI location.

    Args:
        poi_id: POI ID obtained from search results

    Returns:
        JSON string containing detailed place information
    """
    try:
        logger.info(f"🔍 Getting place detail: {poi_id}")

        client = get_amap_client()
        result = client.get_place_detail(poi_id)

        logger.info(f"🔍 Got place detail")

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        error_msg = f"Failed to get place detail: {str(e)}"
        logger.error(f"❌ {error_msg}")

        return json.dumps({
            "error": error_msg,
            "poi_id": poi_id
        }, ensure_ascii=False)
