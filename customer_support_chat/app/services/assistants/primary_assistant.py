from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate
from customer_support_chat.app.services.tools import (
    lookup_policy,
)
# Import Aviation MCP tools
from customer_support_chat.app.services.tools.aviation_mcp_tools import (
    get_today_date,
    search_flights_realtime,
    search_flight_by_number,
    get_flight_transfer_info,
    get_flight_happiness_index,
    get_airport_weather,
    search_flight_itineraries,
    get_flight_prices,
    get_realtime_aircraft_location,
)
# Import RollingGo Hotel MCP tools
from customer_support_chat.app.services.tools.rollinggo_hotel_tools import (
    search_hotels,
    get_hotel_detail,
    get_hotel_static_info,
    get_hotel_search_tags,
)
# Import AMap (高德地图) MCP tools
from customer_support_chat.app.services.tools.amap_route_tools import (
    geocode_address,
    reverse_geocode,
    plan_walking_route,
    plan_bicycling_route,
    plan_driving_route,
    plan_transit_route,
    measure_distance,
    search_place_by_keyword,
    search_nearby_places,
    get_place_detail,
)
from langchain_community.tools.ddg_search.tool import DuckDuckGoSearchResults
from customer_support_chat.app.services.assistants.assistant_base import Assistant, llm
from customer_support_chat.app.core.state import State
from pydantic import BaseModel, Field

# Import new delegation models
from customer_support_chat.app.services.assistants.woocommerce_assistant import ToWooCommerceProducts, ToWooCommerceOrders
from customer_support_chat.app.services.assistants.form_submission_assistant import ToFormSubmission
from customer_support_chat.app.services.assistants.blog_search_assistant import ToBlogSearch

# Define task delegation tools
class ToFlightBookingAssistant(BaseModel):
    """Transfers work to a specialized assistant to handle flight updates and cancellations."""
    request: str = Field(description="Any necessary follow-up questions the update flight assistant should clarify before proceeding.")

class ToBookCarRental(BaseModel):
    """Transfers work to a specialized assistant to handle car rental bookings."""
    location: str = Field(description="The location where the user wants to rent a car.")
    start_date: str = Field(description="The start date of the car rental.")
    end_date: str = Field(description="The end date of the car rental.")
    request: str = Field(description="Any additional information or requests from the user regarding the car rental.")

class ToHotelBookingAssistant(BaseModel):
    """Transfers work to a specialized assistant to handle hotel bookings, modifications, and cancellations."""
    location: str = Field(description="The location where the user wants to book a hotel. Use 'Unknown' if not specified for cancellation requests.", default="Unknown")
    checkin_date: str = Field(description="The check-in date for the hotel. Use 'Unknown' if not specified for cancellation requests.", default="Unknown")
    checkout_date: str = Field(description="The check-out date for the hotel. Use 'Unknown' if not specified for cancellation requests.", default="Unknown")
    request: str = Field(description="Any additional information or requests from the user regarding the hotel operation (booking, cancellation, modification).")

class ToBookExcursion(BaseModel):
    """Transfers work to a specialized assistant to handle trip recommendation and other excursion bookings."""
    location: str = Field(description="The location where the user wants to book a recommended trip.")
    request: str = Field(description="Any additional information or requests from the user regarding the trip recommendation.")

# Primary assistant prompt
primary_assistant_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful customer support assistant for Swiss Airlines. "
            "Your primary role is to search for flight, hotel, and route planning information to answer customer queries. "
            "\n\n=== REAL-TIME FLIGHT TOOLS ==="
            "\nYou have access to comprehensive real-time flight data through Aviation MCP:"
            "\n\n**Date Handling:**"
            "\n1. ALWAYS call get_today_date() FIRST to get the current date"
            "\n2. Calculate dates based on the current date (e.g., 'tomorrow' = today + 1 day)"
            "\n3. Date format must be YYYY-MM-DD"
            "\n\n**City/Airport Codes:**"
            "\n- Use IATA three-letter codes: 北京→BJS, 上海→SHA, 重庆→CKG, 广州→CAN, 深圳→SZX"
            "\n  成都→CTU, 杭州→HGH, 西安→SIA, 南京→NKG, 武汉→WUH"
            "\n\n**Available Flight Tools:**"
            "\n1. search_flights_realtime - Direct flight search"
            "\n2. search_flight_itineraries - Quick recommendations with prices"
            "\n3. get_flight_prices - Detailed pricing by cabin class"
            "\n4. get_flight_transfer_info - Connecting flights"
            "\n5. search_flight_by_number - Look up specific flight"
            "\n6. get_flight_happiness_index - Comfort info (on-time rate, seats, meals)"
            "\n7. get_airport_weather - 3-day weather forecast"
            "\n8. get_realtime_aircraft_location - Track aircraft by tail number"
            "\n\n=== REAL-TIME HOTEL TOOLS ==="
            "\nYou have access to real-time hotel data through RollingGo MCP:"
            "\n\n**Available Hotel Tools:**"
            "\n1. search_hotels - Search by location, dates, star rating, price"
            "\n2. get_hotel_detail - Get detailed info (rooms, prices)"
            "\n3. get_hotel_static_info - Get facilities, policies, photos"
            "\n4. get_hotel_search_tags - Get available filter tags"
            "\n\n=== ROUTE PLANNING & NAVIGATION TOOLS ==="
            "\nYou have access to route planning through AMap (高德地图) MCP:"
            "\n\n**IMPORTANT: Location Requirements**"
            "\nMost route planning tools require GPS coordinates (经纬度) in format 'longitude,latitude'"
            "\n- If user provides place names, use geocode_address or search_place_by_keyword FIRST"
            "\n- Example workflow:"
            "\n  User: '从北京站到天安门怎么走？'"
            "\n  Step 1: search_place_by_keyword('北京站', '北京') → get coordinates"
            "\n  Step 2: search_place_by_keyword('天安门', '北京') → get coordinates"
            "\n  Step 3: plan_walking_route(origin_coords, dest_coords)"
            "\n\n**Available Route Planning Tools:**"
            "\n1. geocode_address - Convert address to GPS coordinates (地址→经纬度)"
            "\n2. reverse_geocode - Convert GPS to address (经纬度→地址)"
            "\n3. search_place_by_keyword - Search places by keyword (get coordinates)"
            "\n4. search_nearby_places - Find nearby POIs"
            "\n5. get_place_detail - Get detailed place information"
            "\n6. plan_walking_route - Plan walking route (步行路线，最大100km)"
            "\n7. plan_bicycling_route - Plan bicycling route (骑行路线，最大500km)"
            "\n8. plan_driving_route - Plan driving route (驾车路线)"
            "\n9. plan_transit_route - Plan public transit route (公交/地铁路线)"
            "\n10. measure_distance - Measure distance between two points"
            "\n\n**Route Planning Examples:**"
            "\n- User: '从北京站到天安门怎么走？'"
            "\n  → Step 1: search_place_by_keyword('北京站') to get origin coordinates"
            "\n  → Step 2: search_place_by_keyword('天安门') to get destination coordinates"
            "\n  → Step 3: plan_walking_route(origin, destination)"
            "\n- User: '西湖附近有什么餐厅？'"
            "\n  → Step 1: search_place_by_keyword('西湖', '杭州') to get location"
            "\n  → Step 2: search_nearby_places('餐厅', location, radius=1000)"
            "\n\n**Tool Selection Strategy:**"
            "\n- User asks about flights → use Aviation MCP tools"
            "\n- User asks about hotels → use RollingGo Hotel MCP tools"
            "\n- User asks 'how to get from A to B' → use AMap route planning"
            "\n- User asks 'walking/driving/transit route' → use appropriate plan_*_route tool"
            "\n- User asks 'nearby places' → use search_nearby_places"
            "\n- User asks 'where is X' → use search_place_by_keyword"
            "\n\nWhen customers need help with specialized services, you must delegate to the appropriate assistant: "
            "\n\nDELEGATION RULES (ALWAYS delegate, never try to handle these yourself):"
            "- Flight updates/cancellations → ToFlightBookingAssistant"
            "- Car rental booking/modification/cancellation → ToBookCarRental"
            "- Hotel booking/modification/cancellation/status → ToHotelBookingAssistant"
            "- Trip recommendations/excursions → ToBookExcursion"
            "- Product searches → ToWooCommerceProducts"
            "- Order searches → ToWooCommerceOrders"
            "- Form submissions → ToFormSubmission"
            "- Blog searches → ToBlogSearch"
            "\n\nIMPORTANT: If the user asks about MULTIPLE services in one query, "
            "do NOT delegate to multiple assistants. Instead, handle it yourself and ask the user to specify."
            "\n\nOnly delegate to ONE assistant at a time. Never make multiple delegation calls in a single response."
            "\n\nProvide detailed information to the customer, and always double-check before concluding that information is unavailable. "
            "When searching, be persistent. Expand your query bounds if the first search returns no results."
            "\n\nCurrent user flight information:\n<Flights>\n{user_info}\n</Flights>"
            "\nCurrent time: {time}.",
        ),
        ("placeholder", "{messages}"),
    ]
).partial(time=datetime.now())

# Primary assistant tools
primary_assistant_tools = [
    DuckDuckGoSearchResults(max_results=10),
    get_today_date,
    # Aviation MCP tools
    search_flights_realtime,
    search_flight_by_number,
    get_flight_transfer_info,
    get_flight_happiness_index,
    get_airport_weather,
    search_flight_itineraries,
    get_flight_prices,
    get_realtime_aircraft_location,
    # RollingGo Hotel MCP tools
    search_hotels,
    get_hotel_detail,
    get_hotel_static_info,
    get_hotel_search_tags,
    # AMap (高德地图) MCP tools - Route Planning
    geocode_address,
    reverse_geocode,
    plan_walking_route,
    plan_bicycling_route,
    plan_driving_route,
    plan_transit_route,
    measure_distance,
    search_place_by_keyword,
    search_nearby_places,
    get_place_detail,
    # Other tools
    lookup_policy,
    ToFlightBookingAssistant,
    ToBookCarRental,  # Keep for backward compatibility but functionality replaced by AMap
    ToHotelBookingAssistant,
    ToBookExcursion,
    # New tools for delegation
    ToWooCommerceProducts,
    ToWooCommerceOrders,
    ToFormSubmission,
    ToBlogSearch,
]

# Create the primary assistant runnable
primary_assistant_runnable = primary_assistant_prompt | llm.bind_tools(primary_assistant_tools)

# Instantiate the primary assistant
primary_assistant = Assistant(primary_assistant_runnable)