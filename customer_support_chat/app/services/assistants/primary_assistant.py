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
            "Your primary role is to search for flight information and company policies to answer customer queries. "
            "\n\n=== REAL-TIME FLIGHT SEARCH ==="
            "\nYou have access to real-time flight data through Aviation MCP. When searching for flights:"
            "\n1. ALWAYS call get_today_date() FIRST to get the current date"
            "\n2. Calculate dates based on the current date (e.g., 'tomorrow' = today + 1 day)"
            "\n3. Use IATA three-letter city codes when calling search_flights_realtime:"
            "\n   - Common Chinese cities: 北京→BJS, 上海→SHA, 重庆→CKG, 广州→CAN, 深圳→SZX"
            "\n     成都→CTU, 杭州→HGH, 西安→SIA, 南京→NKG, 武汉→WUH"
            "\n   - If user provides Chinese city names, the tool will auto-convert them"
            "\n4. Date format must be YYYY-MM-DD"
            "\n5. The tool returns real-time flight data including flight numbers, times, aircraft types, and status"
            "\n\nExample workflow for 'tomorrow Shanghai to Beijing flights':"
            "\n- Step 1: Call get_today_date() → returns '2026-11-10'"
            "\n- Step 2: Calculate tomorrow = '2026-11-11'"
            "\n- Step 3: Call search_flights_realtime(departure_city='SHA', arrival_city='BJS', date='2026-11-11')"
            "\n\nWhen customers need help with specialized services, you must delegate to the appropriate assistant: "
            "\n\nDELEGATION RULES (ALWAYS delegate, never try to handle these yourself):"
            "- Flight updates/cancellations → ToFlightBookingAssistant"
            "- Car rental booking/modification/cancellation → ToBookCarRental"
            "- Hotel booking/modification/cancellation/status → ToHotelBookingAssistant"
            "- Trip recommendations/excursions → ToBookExcursion"
            # New delegation rules
            "- Product searches → ToWooCommerceProducts"
            "- Order searches (with email/name verification) → ToWooCommerceOrders"
            "- Form submissions → ToFormSubmission"
            "- Blog searches → ToBlogSearch"
            "\n\nFor hotel operations, delegate even for:"
            "- 'cancel my hotel', 'cancel it' (when referring to hotel)"
            "- 'check hotel status', 'hotel booking status'"
            "- 'modify my hotel booking', 'change hotel dates'"
            "\n\nIMPORTANT: If the user asks about MULTIPLE services in one query (e.g., 'car and hotel status'), "
            "do NOT delegate to multiple assistants. Instead, handle it yourself by:"
            "1. Using search_flights_realtime to check available flights"
            "2. Providing a summary of what you can see"
            "3. Asking the user to specify which service they want detailed help with"
            "\n\nOnly delegate to ONE assistant at a time. Never make multiple delegation calls in a single response."
            "\n\nOnly the specialized assistants have permission to make these changes. "
            "The user is not aware of the different specialized assistants, so do not mention them; just quietly delegate through function calls. "
            "Provide detailed information to the customer, and always double-check the database before concluding that information is unavailable. "
            "When searching, be persistent. Expand your query bounds if the first search returns no results. "
            "If a search comes up empty, expand your search before giving up."
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
    search_flights_realtime,
    search_flight_by_number,
    lookup_policy,
    ToFlightBookingAssistant,
    ToBookCarRental,
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