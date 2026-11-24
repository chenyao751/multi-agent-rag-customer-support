"""RollingGo Hotel MCP Tools

LangChain tool wrappers for RollingGo Hotel MCP service.
"""

import json
from typing import Optional, List
from langchain_core.tools import tool
from customer_support_chat.app.core.logger import logger
from customer_support_chat.app.services.integrations.rollinggo_mcp_client import get_rollinggo_client


@tool
def search_hotels(
    place: str,
    check_in_date: str,
    stay_nights: int = 1,
    adult_count: int = 2,
    star_ratings: Optional[List[float]] = None,
    max_price_per_night: Optional[float] = None,
    size: int = 5,
    place_type: str = "城市"
) -> str:
    """Search for hotels based on location, dates, and preferences.

    Args:
        place: Place name (city, landmark, or business district in Chinese, e.g., '杭州', '西湖')
        check_in_date: Check-in date in YYYY-MM-DD format
        stay_nights: Number of nights to stay (default 1)
        adult_count: Number of adults (default 2)
        star_ratings: List of star ratings to filter (e.g., [4.0, 5.0] for 4-5 star hotels)
        max_price_per_night: Maximum price per night in CNY
        size: Number of results to return (default 5)
        place_type: Type of place - '城市' (city), '商圈' (business district), '景点' (landmark)

    Returns:
        JSON string containing hotel search results with booking URLs
    """
    try:
        logger.info(f"🏨 Searching hotels in {place} for {check_in_date}, {stay_nights} nights")

        client = get_rollinggo_client()

        # Build filter options
        filter_options = {}
        if star_ratings:
            filter_options["starRatings"] = star_ratings

        # Build hotel tags
        hotel_tags = {}
        if max_price_per_night:
            hotel_tags["maxPricePerNight"] = max_price_per_night

        arguments = {
            "originQuery": f"{place}附近的酒店，{check_in_date}入住{stay_nights}晚",
            "place": place,
            "placeType": place_type,
            "checkInParam": {
                "checkInDate": check_in_date,
                "stayNights": stay_nights,
                "adultCount": adult_count
            },
            "size": size
        }

        if filter_options:
            arguments["filterOptions"] = filter_options

        if hotel_tags:
            arguments["hotelTags"] = hotel_tags

        result = client.call_tool("searchHotels", arguments)

        logger.info(f"🏨 Found hotels in {place}")

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        error_msg = f"Failed to search hotels: {str(e)}"
        logger.error(f"❌ {error_msg}")

        return json.dumps({
            "error": error_msg,
            "place": place,
            "check_in_date": check_in_date
        }, ensure_ascii=False)


@tool
def get_hotel_detail(
    hotel_id: int,
    check_in_date: str,
    stay_nights: int = 1,
    adult_count: int = 2
) -> str:
    """Get detailed information about a specific hotel including room types and pricing.

    Args:
        hotel_id: Hotel ID from search results
        check_in_date: Check-in date in YYYY-MM-DD format
        stay_nights: Number of nights to stay (default 1)
        adult_count: Number of adults (default 2)

    Returns:
        JSON string containing detailed hotel information, room types, and booking URLs
    """
    try:
        logger.info(f"🏨 Getting details for hotel {hotel_id}")

        client = get_rollinggo_client()

        arguments = {
            "hotelId": hotel_id,
            "checkInParam": {
                "checkInDate": check_in_date,
                "stayNights": stay_nights,
                "adultCount": adult_count
            }
        }

        result = client.call_tool("getHotelDetail", arguments)

        logger.info(f"🏨 Got details for hotel {hotel_id}")

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        error_msg = f"Failed to get hotel detail: {str(e)}"
        logger.error(f"❌ {error_msg}")

        return json.dumps({
            "error": error_msg,
            "hotel_id": hotel_id
        }, ensure_ascii=False)


@tool
def get_hotel_static_info(
    hotel_id: int,
    info_types: Optional[List[str]] = None
) -> str:
    """Get static information about a hotel (facilities, policies, location, photos).

    Args:
        hotel_id: Hotel ID
        info_types: List of info types to retrieve. Options:
            - 'basic': Basic information
            - 'location': Location details
            - 'policies': Hotel policies
            - 'facilities': Facilities and amenities
            - 'photos': Hotel photos
            - 'tags': Feature tags
            If None, returns all information.

    Returns:
        JSON string containing hotel static information
    """
    try:
        logger.info(f"🏨 Getting static info for hotel {hotel_id}")

        client = get_rollinggo_client()

        arguments = {
            "hotelId": hotel_id
        }

        if info_types:
            arguments["infoTypes"] = info_types

        result = client.call_tool("getHotelStaticInfo", arguments)

        logger.info(f"🏨 Got static info for hotel {hotel_id}")

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        error_msg = f"Failed to get hotel static info: {str(e)}"
        logger.error(f"❌ {error_msg}")

        return json.dumps({
            "error": error_msg,
            "hotel_id": hotel_id
        }, ensure_ascii=False)


@tool
def get_hotel_search_tags() -> str:
    """Get all available hotel feature tags supported by the platform.

    Use this to understand what tags users can filter by, such as:
    - Free WiFi
    - Swimming pool
    - Family-friendly
    - Near subway
    - Breakfast included
    etc.

    Returns:
        JSON string containing list of all supported hotel tags
    """
    try:
        logger.info(f"🏨 Getting hotel search tags")

        client = get_rollinggo_client()

        result = client.call_tool("getHotelSearchTags", {})

        logger.info(f"🏨 Got hotel search tags")

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        error_msg = f"Failed to get hotel search tags: {str(e)}"
        logger.error(f"❌ {error_msg}")

        return json.dumps({
            "error": error_msg
        }, ensure_ascii=False)
