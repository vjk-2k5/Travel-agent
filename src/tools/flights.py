"""
Flight-related tools with mock data.
Provides flight search, pricing, and booking functionality.
"""

import uuid
from datetime import datetime, timedelta
from typing import Any

from ..utils.logger import get_logger


# Mock flight data
MOCK_AIRLINES = [
    {"code": "SQ", "name": "Singapore Airlines"},
    {"code": "AI", "name": "Air India"},
    {"code": "6E", "name": "IndiGo"},
    {"code": "UK", "name": "Vistara"},
    {"code": "EK", "name": "Emirates"},
    {"code": "QR", "name": "Qatar Airways"},
]

# Price ranges by cabin class (in INR for base)
PRICE_RANGES = {
    "ECONOMY": (15000, 35000),
    "PREMIUM_ECONOMY": (35000, 55000),
    "BUSINESS": (80000, 150000),
    "FIRST": (200000, 400000)
}


def _generate_flight_offer_id() -> str:
    """Generate a unique flight offer ID."""
    return f"FLT-{uuid.uuid4().hex[:8].upper()}"


def _generate_mock_flights(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: str | None,
    adults: int,
    cabin_class: str
) -> list[dict]:
    """Generate realistic mock flight data."""
    import random
    
    flights = []
    num_options = random.randint(3, 6)
    
    for i in range(num_options):
        airline = random.choice(MOCK_AIRLINES)
        price_range = PRICE_RANGES.get(cabin_class, PRICE_RANGES["ECONOMY"])
        base_price = random.randint(price_range[0], price_range[1])
        
        # Parse departure date
        dep_date = datetime.strptime(departure_date, "%Y-%m-%d")
        
        # Generate departure and arrival times
        dep_hour = random.randint(6, 22)
        flight_duration_hours = random.randint(4, 8)
        
        dep_time = dep_date.replace(hour=dep_hour, minute=random.choice([0, 15, 30, 45]))
        arr_time = dep_time + timedelta(hours=flight_duration_hours, minutes=random.randint(0, 45))
        
        flight_offer = {
            "offer_id": _generate_flight_offer_id(),
            "airline": {
                "code": airline["code"],
                "name": airline["name"]
            },
            "itinerary": {
                "outbound": {
                    "departure": {
                        "airport": origin,
                        "datetime": dep_time.strftime("%Y-%m-%dT%H:%M:%S")
                    },
                    "arrival": {
                        "airport": destination,
                        "datetime": arr_time.strftime("%Y-%m-%dT%H:%M:%S")
                    },
                    "duration": f"PT{flight_duration_hours}H{random.randint(0, 45)}M",
                    "stops": random.choice([0, 0, 0, 1])  # Mostly direct
                }
            },
            "cabin_class": cabin_class,
            "passengers": adults,
            "price": {
                "base": base_price * adults,
                "taxes": int(base_price * adults * 0.12),
                "total": int(base_price * adults * 1.12),
                "currency": "INR"
            },
            "seats_available": random.randint(2, 15)
        }
        
        # Add return flight if round trip
        if return_date:
            ret_date = datetime.strptime(return_date, "%Y-%m-%d")
            ret_hour = random.randint(6, 22)
            ret_time = ret_date.replace(hour=ret_hour, minute=random.choice([0, 15, 30, 45]))
            ret_arr_time = ret_time + timedelta(hours=flight_duration_hours, minutes=random.randint(0, 45))
            
            flight_offer["itinerary"]["return"] = {
                "departure": {
                    "airport": destination,
                    "datetime": ret_time.strftime("%Y-%m-%dT%H:%M:%S")
                },
                "arrival": {
                    "airport": origin,
                    "datetime": ret_arr_time.strftime("%Y-%m-%dT%H:%M:%S")
                },
                "duration": f"PT{flight_duration_hours}H{random.randint(0, 45)}M",
                "stops": random.choice([0, 0, 0, 1])
            }
            # Double the price for round trip
            flight_offer["price"]["base"] *= 2
            flight_offer["price"]["taxes"] *= 2
            flight_offer["price"]["total"] *= 2
        
        flights.append(flight_offer)
    
    # Sort by price
    flights.sort(key=lambda x: x["price"]["total"])
    return flights


def search_flights(
    origin: str,
    destination: str,
    departure_date: str,
    adults: int,
    return_date: str | None = None,
    cabin_class: str = "ECONOMY"
) -> dict[str, Any]:
    """
    Search for available flights between two airports.
    Uses FlightAPI.io for real data when available, falls back to mock data.
    
    Args:
        origin: Origin airport IATA code
        destination: Destination airport IATA code
        departure_date: Departure date (YYYY-MM-DD)
        adults: Number of adult passengers
        return_date: Return date for round trip (optional)
        cabin_class: Cabin class preference
    
    Returns:
        Dictionary with flight search results
    """
    import os
    
    logger = get_logger()
    
    params = {
        "origin": origin,
        "destination": destination,
        "departure_date": departure_date,
        "return_date": return_date,
        "adults": adults,
        "cabin_class": cabin_class
    }
    
    # Try to use FlightAPI if key is available
    flight_api_key = os.getenv("FLIGHT_API")
    if flight_api_key:
        try:
            from ..api.flightapi import search_flights_real
            
            # Map cabin class to FlightAPI format
            cabin_map = {
                "ECONOMY": "Economy",
                "PREMIUM_ECONOMY": "Premium_Economy",
                "BUSINESS": "Business",
                "FIRST": "First"
            }
            api_cabin = cabin_map.get(cabin_class, "Economy")
            
            result = search_flights_real(
                origin=origin,
                destination=destination,
                departure_date=departure_date,
                adults=adults,
                children=0,
                infants=0,
                cabin_class=api_cabin,
                currency="INR",
                return_date=return_date
            )
            
            if result.get("success") and result.get("flights"):
                # Transform to expected format
                flights = result.get("flights", [])
                transformed_flights = []
                for f in flights:
                    transformed_flights.append({
                        "offer_id": f.get("offer_id", _generate_flight_offer_id()),
                        "airline": f.get("airline", {"code": "??", "name": "Unknown"}),
                        "itinerary": {
                            "outbound": {
                                "departure": {
                                    "airport": origin,
                                    "datetime": f.get("legs", [{}])[0].get("departure", "")
                                },
                                "arrival": {
                                    "airport": destination,
                                    "datetime": f.get("legs", [{}])[0].get("arrival", "")
                                },
                                "duration_minutes": f.get("total_duration_minutes", 0),
                                "stops": f.get("stops", 0)
                            }
                        },
                        "cabin_class": cabin_class,
                        "passengers": adults,
                        "price": {
                            "base": int(f.get("price", {}).get("amount", 0) * 0.88),
                            "taxes": int(f.get("price", {}).get("amount", 0) * 0.12),
                            "total": int(f.get("price", {}).get("amount", 0)),
                            "currency": f.get("price", {}).get("currency", "INR")
                        },
                        "booking_url": f.get("booking_url", ""),
                        "seats_available": 9
                    })
                
                final_result = {
                    "success": True,
                    "source": "flightapi.io",
                    "search_id": f"SRCH-{uuid.uuid4().hex[:8].upper()}",
                    "query": params,
                    "results_count": len(transformed_flights),
                    "flights": transformed_flights
                }
                logger.log("search_flights", params, {"success": True, "source": "flightapi.io", "count": len(transformed_flights)})
                return final_result
        except Exception as e:
            # Log error and fall back to mock data
            logger.log("search_flights", params, {"fallback": "mock", "reason": str(e)}, success=True)
    
    # Fallback to mock data
    flights = _generate_mock_flights(
        origin, destination, departure_date, return_date, adults, cabin_class
    )
    
    result = {
        "success": True,
        "source": "mock",
        "search_id": f"SRCH-{uuid.uuid4().hex[:8].upper()}",
        "query": params,
        "results_count": len(flights),
        "flights": flights
    }
    
    logger.log("search_flights", params, result)
    return result


def get_flight_pricing(
    flight_offer_id: str,
    currency: str = "INR"
) -> dict[str, Any]:
    """
    Get confirmed pricing for a specific flight offer.
    
    Args:
        flight_offer_id: The flight offer ID from search results
        currency: Currency code for pricing
    
    Returns:
        Dictionary with confirmed pricing details
    """
    import random
    
    logger = get_logger()
    params = {"flight_offer_id": flight_offer_id, "currency": currency}
    
    # Generate mock pricing confirmation
    base_price = random.randint(25000, 80000)
    
    result = {
        "success": True,
        "offer_id": flight_offer_id,
        "pricing_confirmed": True,
        "price": {
            "base": base_price,
            "taxes": int(base_price * 0.12),
            "fees": {
                "fuel_surcharge": int(base_price * 0.05),
                "booking_fee": 500
            },
            "total": int(base_price * 1.17) + 500,
            "currency": currency
        },
        "valid_until": (datetime.now() + timedelta(hours=24)).isoformat(),
        "fare_rules": {
            "cancellation": "Cancellation allowed with fee",
            "changes": "Changes allowed with fee",
            "refundable": False
        }
    }
    
    logger.log("get_flight_pricing", params, result)
    return result


def book_flight(
    flight_offer_id: str,
    passengers: list[dict],
    dry_run: bool = False
) -> dict[str, Any]:
    """
    Book a flight reservation.
    
    Args:
        flight_offer_id: The flight offer ID to book
        passengers: List of passenger details
        dry_run: If True, simulate without actual booking
    
    Returns:
        Dictionary with booking confirmation or dry-run preview
    """
    logger = get_logger()
    
    params = {
        "flight_offer_id": flight_offer_id,
        "passengers": passengers,
        "dry_run": dry_run
    }
    
    booking_ref = f"BK-{uuid.uuid4().hex[:6].upper()}"
    
    if dry_run:
        result = {
            "success": True,
            "status": "DRY_RUN",
            "message": "This is a preview. No actual booking was made.",
            "preview": {
                "booking_reference": booking_ref,
                "flight_offer_id": flight_offer_id,
                "passengers": len(passengers),
                "passenger_names": [
                    f"{p.get('first_name', '')} {p.get('last_name', '')}"
                    for p in passengers
                ]
            }
        }
    else:
        result = {
            "success": True,
            "status": "CONFIRMED",
            "booking_reference": booking_ref,
            "flight_offer_id": flight_offer_id,
            "passengers": [
                {
                    "name": f"{p.get('first_name', '')} {p.get('last_name', '')}",
                    "ticket_number": f"098-{uuid.uuid4().hex[:10].upper()}"
                }
                for p in passengers
            ],
            "confirmation_email_sent": True,
            "created_at": datetime.now().isoformat()
        }
    
    audit_id = logger.log("book_flight", params, result)
    result["audit_log_id"] = audit_id
    return result
