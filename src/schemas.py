"""
JSON schemas for Groq function calling.
Defines all travel-related tool schemas with strict validation.
"""

# Tool definitions for Groq function calling
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "search_flights",
            "description": "Search for available flights between two airports. Returns a list of flight options with pricing.",
            "parameters": {
                "type": "object",
                "properties": {
                    "origin": {
                        "type": "string",
                        "description": "Origin airport IATA code (3 letters, e.g., 'MAA' for Chennai)",
                        "pattern": "^[A-Z]{3}$"
                    },
                    "destination": {
                        "type": "string",
                        "description": "Destination airport IATA code (3 letters, e.g., 'SIN' for Singapore)",
                        "pattern": "^[A-Z]{3}$"
                    },
                    "departure_date": {
                        "type": "string",
                        "description": "Departure date in ISO-8601 format (YYYY-MM-DD)",
                        "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                    },
                    "return_date": {
                        "type": "string",
                        "description": "Return date in ISO-8601 format (YYYY-MM-DD). Optional for one-way flights.",
                        "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                    },
                    "adults": {
                        "type": "integer",
                        "description": "Number of adult passengers (1-9)",
                        "minimum": 1,
                        "maximum": 9
                    },
                    "cabin_class": {
                        "type": "string",
                        "description": "Cabin class preference",
                        "enum": ["ECONOMY", "PREMIUM_ECONOMY", "BUSINESS", "FIRST"]
                    }
                },
                "required": ["origin", "destination", "departure_date", "adults"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_flight_pricing",
            "description": "Get confirmed pricing for a specific flight offer including taxes and fees.",
            "parameters": {
                "type": "object",
                "properties": {
                    "flight_offer_id": {
                        "type": "string",
                        "description": "The unique identifier of the flight offer from search results"
                    },
                    "currency": {
                        "type": "string",
                        "description": "Currency code for pricing (e.g., 'INR', 'USD')",
                        "pattern": "^[A-Z]{3}$"
                    }
                },
                "required": ["flight_offer_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_hotels",
            "description": "Search for available hotels in a city or near a location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city_code": {
                        "type": "string",
                        "description": "City IATA code (e.g., 'SIN' for Singapore)"
                    },
                    "location": {
                        "type": "string",
                        "description": "Location name or landmark (e.g., 'Marina Bay')"
                    },
                    "check_in": {
                        "type": "string",
                        "description": "Check-in date in ISO-8601 format (YYYY-MM-DD)",
                        "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                    },
                    "check_out": {
                        "type": "string",
                        "description": "Check-out date in ISO-8601 format (YYYY-MM-DD)",
                        "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                    },
                    "adults": {
                        "type": "integer",
                        "description": "Number of adult guests",
                        "minimum": 1,
                        "maximum": 9
                    },
                    "rooms": {
                        "type": "integer",
                        "description": "Number of rooms needed",
                        "minimum": 1,
                        "maximum": 9
                    },
                    "amenities": {
                        "type": "array",
                        "description": "Desired amenities (e.g., ['WIFI', 'POOL', 'GYM'])",
                        "items": {"type": "string"}
                    }
                },
                "required": ["check_in", "check_out", "adults"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_hotel_availability",
            "description": "Check room availability for a specific hotel.",
            "parameters": {
                "type": "object",
                "properties": {
                    "hotel_id": {
                        "type": "string",
                        "description": "The unique identifier of the hotel"
                    },
                    "check_in": {
                        "type": "string",
                        "description": "Check-in date in ISO-8601 format",
                        "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                    },
                    "check_out": {
                        "type": "string",
                        "description": "Check-out date in ISO-8601 format",
                        "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                    },
                    "rooms": {
                        "type": "integer",
                        "description": "Number of rooms to check",
                        "minimum": 1,
                        "maximum": 9
                    }
                },
                "required": ["hotel_id", "check_in", "check_out"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "estimate_total_cost",
            "description": "Calculate the total estimated cost for a trip including flights and hotels.",
            "parameters": {
                "type": "object",
                "properties": {
                    "flight_price": {
                        "type": "number",
                        "description": "Total flight cost"
                    },
                    "hotel_price": {
                        "type": "number",
                        "description": "Total hotel cost"
                    },
                    "currency": {
                        "type": "string",
                        "description": "Currency code (e.g., 'INR')",
                        "pattern": "^[A-Z]{3}$"
                    },
                    "include_taxes": {
                        "type": "boolean",
                        "description": "Whether prices include taxes",
                        "default": True
                    },
                    "additional_costs": {
                        "type": "object",
                        "description": "Any additional costs (transfers, activities, etc.)",
                        "additionalProperties": {"type": "number"}
                    }
                },
                "required": ["flight_price", "hotel_price", "currency"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "book_flight",
            "description": "Book a flight. Use dry_run=true to preview without actual booking.",
            "parameters": {
                "type": "object",
                "properties": {
                    "flight_offer_id": {
                        "type": "string",
                        "description": "The flight offer ID to book"
                    },
                    "passengers": {
                        "type": "array",
                        "description": "List of passenger details",
                        "items": {
                            "type": "object",
                            "properties": {
                                "first_name": {"type": "string"},
                                "last_name": {"type": "string"},
                                "date_of_birth": {"type": "string", "pattern": "^\\d{4}-\\d{2}-\\d{2}$"},
                                "passport_number": {"type": "string"},
                                "email": {"type": "string"},
                                "phone": {"type": "string"}
                            },
                            "required": ["first_name", "last_name"]
                        }
                    },
                    "dry_run": {
                        "type": "boolean",
                        "description": "If true, simulate booking without actual reservation",
                        "default": False
                    }
                },
                "required": ["flight_offer_id", "passengers"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "book_hotel",
            "description": "Book a hotel room. Use dry_run=true to preview without actual booking.",
            "parameters": {
                "type": "object",
                "properties": {
                    "hotel_offer_id": {
                        "type": "string",
                        "description": "The hotel offer ID to book"
                    },
                    "guests": {
                        "type": "array",
                        "description": "List of guest details",
                        "items": {
                            "type": "object",
                            "properties": {
                                "first_name": {"type": "string"},
                                "last_name": {"type": "string"},
                                "email": {"type": "string"},
                                "phone": {"type": "string"}
                            },
                            "required": ["first_name", "last_name"]
                        }
                    },
                    "payment_info": {
                        "type": "object",
                        "description": "Payment details (required for actual booking)",
                        "properties": {
                            "card_type": {"type": "string"},
                            "card_last_four": {"type": "string"}
                        }
                    },
                    "dry_run": {
                        "type": "boolean",
                        "description": "If true, simulate booking without actual reservation",
                        "default": False
                    }
                },
                "required": ["hotel_offer_id", "guests"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "plan_destination",
            "description": "Create an AI-powered day-by-day itinerary for a destination with places to visit, local tips, and recommendations. Uses Mistral 7B AI.",
            "parameters": {
                "type": "object",
                "properties": {
                    "destination": {
                        "type": "string",
                        "description": "The destination city or country to plan for (e.g., 'Singapore', 'Paris', 'Bali')"
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of days for the trip",
                        "minimum": 1,
                        "maximum": 14,
                        "default": 3
                    },
                    "interests": {
                        "type": "array",
                        "description": "List of interests (e.g., ['history', 'food', 'nature', 'shopping', 'nightlife'])",
                        "items": {"type": "string"}
                    },
                    "travel_style": {
                        "type": "string",
                        "description": "Travel style preference",
                        "enum": ["budget", "moderate", "luxury", "adventure", "relaxed", "family"]
                    },
                    "budget": {
                        "type": "string",
                        "description": "Budget level",
                        "enum": ["budget", "moderate", "luxury"]
                    }
                },
                "required": ["destination"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_attractions",
            "description": "Get a list of top attractions and must-visit places for a destination. Uses Mistral 7B AI.",
            "parameters": {
                "type": "object",
                "properties": {
                    "destination": {
                        "type": "string",
                        "description": "The destination to get attractions for"
                    },
                    "category": {
                        "type": "string",
                        "description": "Category filter for attractions",
                        "enum": ["museums", "nature", "food", "shopping", "nightlife", "historical", "family"]
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of attractions to return",
                        "minimum": 1,
                        "maximum": 20,
                        "default": 10
                    }
                },
                "required": ["destination"]
            }
        }
    }
]


def get_tool_schemas() -> list:
    """Return all tool schemas for Groq function calling."""
    return TOOL_SCHEMAS


def get_tool_by_name(name: str) -> dict | None:
    """Get a specific tool schema by name."""
    for tool in TOOL_SCHEMAS:
        if tool["function"]["name"] == name:
            return tool
    return None
