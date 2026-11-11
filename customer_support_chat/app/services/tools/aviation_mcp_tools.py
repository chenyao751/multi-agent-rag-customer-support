"""Aviation MCP Tools

LangChain tool wrappers for Aviation MCP service.
"""

import json
from typing import Optional
from langchain_core.tools import tool
from customer_support_chat.app.core.logger import logger
from customer_support_chat.app.services.integrations.aviation_mcp_client import get_mcp_client
from customer_support_chat.app.services.integrations.city_code_mapping import get_city_code


@tool
def get_today_date() -> str:
    """Get today's date to avoid hardcoding dates.

    This tool returns the current date in YYYY-MM-DD format.
    Always call this tool first when the user asks about relative dates like
    'tomorrow', 'next week', etc., to calculate the actual date.

    Returns:
        Today's date in YYYY-MM-DD format
    """
    try:
        client = get_mcp_client()
        result = client.call_tool("getTodayDate", {})

        logger.info(f"✈️ Got today's date: {result}")
        return result

    except Exception as e:
        logger.error(f"Failed to get today's date from Aviation MCP: {e}")
        # Fallback to local date
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        logger.info(f"Using local date as fallback: {today}")
        return today


@tool
def search_flights_realtime(
    departure_city: str,
    arrival_city: str,
    date: str,
    limit: int = 10
) -> str:
    """Search for real-time flights between two cities.

    IMPORTANT:
    - Cities must use IATA three-letter codes (e.g., SHA for Shanghai, BJS for Beijing, CKG for Chongqing)
    - If user provides Chinese city names, convert them first:
      北京→BJS, 上海→SHA, 重庆→CKG, 广州→CAN, 深圳→SZX, 成都→CTU, 杭州→HGH, 西安→SIA
    - Date must be in YYYY-MM-DD format
    - Use get_today_date() first if the user asks about relative dates

    Args:
        departure_city: Departure city IATA code (e.g., SHA)
        arrival_city: Arrival city IATA code (e.g., BJS)
        date: Flight date in YYYY-MM-DD format
        limit: Maximum number of results (default 10, max 50)

    Returns:
        JSON string containing flight information including:
        - Flight number
        - Departure/arrival airports and times
        - Aircraft type
        - Flight status
        - Check-in counter
    """
    try:
        # Convert Chinese city names to IATA codes if needed
        dep_code = get_city_code(departure_city)
        arr_code = get_city_code(arrival_city)

        logger.info(f"✈️ Searching flights: {dep_code} → {arr_code} on {date} (limit: {limit})")

        client = get_mcp_client()

        arguments = {
            "depcity": dep_code,
            "arrcity": arr_code,
            "date": date,
            "limit": min(limit, 50),  # Cap at 50
            "detail": "summary"  # Use summary for faster response
        }

        result = client.call_tool("searchFlightsByDepArr", arguments)

        # Log success
        logger.info(f"✈️ Found flights from {dep_code} to {arr_code}")

        # Return as JSON string for the AI to parse
        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        error_msg = f"Failed to search flights: {str(e)}"
        logger.error(f"❌ {error_msg}")

        # Return error message in a structured format
        return json.dumps({
            "error": error_msg,
            "departure": departure_city,
            "arrival": arrival_city,
            "date": date
        }, ensure_ascii=False)


@tool
def search_flight_by_number(
    flight_number: str,
    date: str,
    departure_airport: Optional[str] = None,
    arrival_airport: Optional[str] = None
) -> str:
    """Search for a specific flight by flight number.

    Args:
        flight_number: Flight number including airline code (e.g., MU2157, CA1234)
        date: Flight date in YYYY-MM-DD format
        departure_airport: Optional departure airport IATA code
        arrival_airport: Optional arrival airport IATA code

    Returns:
        JSON string containing detailed flight information
    """
    try:
        logger.info(f"✈️ Searching flight by number: {flight_number} on {date}")

        client = get_mcp_client()

        arguments = {
            "fnum": flight_number,
            "date": date
        }

        if departure_airport:
            arguments["dep"] = get_city_code(departure_airport)

        if arrival_airport:
            arguments["arr"] = get_city_code(arrival_airport)

        result = client.call_tool("searchFlightsByNumber", arguments)

        logger.info(f"✈️ Found flight {flight_number}")

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        error_msg = f"Failed to search flight by number: {str(e)}"
        logger.error(f"❌ {error_msg}")

        return json.dumps({
            "error": error_msg,
            "flight_number": flight_number,
            "date": date
        }, ensure_ascii=False)
