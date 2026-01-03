"""
Hotel-related tools with mock data.
Provides hotel search, availability check, and booking functionality.
"""

import uuid
from datetime import datetime, timedelta
from typing import Any

from ..utils.logger import get_logger


# Mock hotel data by city
MOCK_HOTELS = {
    "SIN": [
        {"id": "HTL-MBS001", "name": "Marina Bay Sands", "rating": 5, "location": "Marina Bay", "base_price": 25000},
        {"id": "HTL-FUL002", "name": "Fullerton Hotel", "rating": 5, "location": "Marina Bay", "base_price": 22000},
        {"id": "HTL-RWS003", "name": "Resorts World Sentosa", "rating": 5, "location": "Sentosa", "base_price": 18000},
        {"id": "HTL-HII004", "name": "Holiday Inn Express", "rating": 3, "location": "Orchard", "base_price": 8000},
        {"id": "HTL-NOV005", "name": "Novotel Singapore", "rating": 4, "location": "Clarke Quay", "base_price": 12000},
    ],
    "DXB": [
        {"id": "HTL-BJA001", "name": "Burj Al Arab", "rating": 5, "location": "Jumeirah", "base_price": 85000},
        {"id": "HTL-ATL002", "name": "Atlantis The Palm", "rating": 5, "location": "Palm Jumeirah", "base_price": 35000},
        {"id": "HTL-JWM003", "name": "JW Marriott Marquis", "rating": 5, "location": "Downtown", "base_price": 18000},
    ],
    "BKK": [
        {"id": "HTL-MND001", "name": "Mandarin Oriental", "rating": 5, "location": "Riverside", "base_price": 15000},
        {"id": "HTL-SHT002", "name": "Shangri-La Hotel", "rating": 5, "location": "Silom", "base_price": 12000},
        {"id": "HTL-IBB003", "name": "ibis Bangkok", "rating": 3, "location": "Sukhumvit", "base_price": 3500},
    ],
    "DEFAULT": [
        {"id": "HTL-GEN001", "name": "Grand Hotel", "rating": 4, "location": "City Center", "base_price": 10000},
        {"id": "HTL-GEN002", "name": "Business Hotel", "rating": 3, "location": "City Center", "base_price": 6000},
        {"id": "HTL-GEN003", "name": "Budget Inn", "rating": 2, "location": "Suburb", "base_price": 3000},
    ]
}

AMENITIES_LIST = ["WIFI", "POOL", "GYM", "SPA", "RESTAURANT", "BAR", "PARKING", "AIRPORT_SHUTTLE", "ROOM_SERVICE"]


def _generate_hotel_offer_id() -> str:
    """Generate a unique hotel offer ID."""
    return f"HOFFER-{uuid.uuid4().hex[:8].upper()}"


def _calculate_nights(check_in: str, check_out: str) -> int:
    """Calculate number of nights between dates."""
    in_date = datetime.strptime(check_in, "%Y-%m-%d")
    out_date = datetime.strptime(check_out, "%Y-%m-%d")
    return (out_date - in_date).days


def search_hotels(
    check_in: str,
    check_out: str,
    adults: int,
    city_code: str | None = None,
    location: str | None = None,
    rooms: int = 1,
    amenities: list[str] | None = None
) -> dict[str, Any]:
    """
    Search for available hotels in a city or near a location.
    Uses SearchAPI.io for real data when available, falls back to mock data.
    
    Args:
        check_in: Check-in date (YYYY-MM-DD)
        check_out: Check-out date (YYYY-MM-DD)
        adults: Number of adult guests
        city_code: City IATA code
        location: Location name or landmark
        rooms: Number of rooms needed
        amenities: Desired amenities
    
    Returns:
        Dictionary with hotel search results
    """
    import os
    import random
    
    logger = get_logger()
    
    params = {
        "city_code": city_code,
        "location": location,
        "check_in": check_in,
        "check_out": check_out,
        "adults": adults,
        "rooms": rooms,
        "amenities": amenities
    }
    
    # Try to use SearchAPI if key is available
    search_api_key = os.getenv("SEARCH_API")
    if search_api_key:
        try:
            from ..api.searchapi import search_hotels_real
            
            # Determine search location
            search_location = location or city_code or "Hotels"
            
            result = search_hotels_real(
                location=search_location,
                check_in=check_in,
                check_out=check_out,
                adults=adults,
                rooms=rooms
            )
            
            if result.get("success"):
                # Transform to expected format if needed
                hotels = result.get("hotels", [])
                transformed_hotels = []
                for h in hotels:
                    transformed_hotels.append({
                        "offer_id": h.get("hotel_id", _generate_hotel_offer_id()),
                        "hotel_id": h.get("hotel_id", ""),
                        "name": h.get("name", "Unknown"),
                        "rating": h.get("rating", 0),
                        "hotel_class": h.get("hotel_class", 0),
                        "location": h.get("location", {}),
                        "check_in": check_in,
                        "check_out": check_out,
                        "nights": _calculate_nights(check_in, check_out),
                        "amenities": h.get("amenities", []),
                        "price": {
                            "per_night_from": h.get("price", {}).get("per_night", 0),
                            "total_from": h.get("price", {}).get("total", 0),
                            "currency": h.get("price", {}).get("currency", "USD")
                        },
                        "deal": h.get("deal"),
                        "nearby_places": h.get("nearby_places", []),
                        "images": h.get("images", [])
                    })
                
                final_result = {
                    "success": True,
                    "source": "searchapi.io",
                    "search_id": f"HSRCH-{uuid.uuid4().hex[:8].upper()}",
                    "query": params,
                    "results_count": len(transformed_hotels),
                    "hotels": transformed_hotels
                }
                logger.log("search_hotels", params, {"success": True, "source": "searchapi.io", "count": len(transformed_hotels)})
                return final_result
        except Exception as e:
            # Log error and fall back to mock data
            logger.log("search_hotels", params, {"fallback": "mock", "reason": str(e)}, success=True)
    
    # Fallback to mock data
    city_key = city_code.upper() if city_code else "DEFAULT"
    hotels_data = MOCK_HOTELS.get(city_key, MOCK_HOTELS["DEFAULT"])
    
    nights = _calculate_nights(check_in, check_out)
    
    hotels = []
    for hotel in hotels_data:
        # Filter by location if specified
        if location and location.lower() not in hotel["location"].lower():
            if random.random() > 0.3:
                continue
        
        base_per_night = hotel["base_price"]
        base_per_night = int(base_per_night * random.uniform(0.9, 1.2))
        total_price = base_per_night * nights * rooms
        
        room_types = []
        for room_type in ["Standard", "Deluxe", "Suite"]:
            multiplier = {"Standard": 1.0, "Deluxe": 1.3, "Suite": 1.8}[room_type]
            room_types.append({
                "type": room_type,
                "price_per_night": int(base_per_night * multiplier),
                "total_price": int(total_price * multiplier),
                "available_rooms": random.randint(1, 5)
            })
        
        hotel_amenities = random.sample(AMENITIES_LIST, random.randint(4, 8))
        
        hotels.append({
            "offer_id": _generate_hotel_offer_id(),
            "hotel_id": hotel["id"],
            "name": hotel["name"],
            "rating": hotel["rating"],
            "location": {
                "area": hotel["location"],
                "city": city_code or "Unknown"
            },
            "check_in": check_in,
            "check_out": check_out,
            "nights": nights,
            "room_options": room_types,
            "amenities": hotel_amenities,
            "price": {
                "per_night_from": base_per_night,
                "total_from": total_price,
                "currency": "INR"
            },
            "cancellation_policy": random.choice([
                "Free cancellation until 24h before",
                "Free cancellation until 48h before",
                "Non-refundable"
            ])
        })
    
    hotels.sort(key=lambda x: x["price"]["total_from"])
    
    result = {
        "success": True,
        "source": "mock",
        "search_id": f"HSRCH-{uuid.uuid4().hex[:8].upper()}",
        "query": params,
        "results_count": len(hotels),
        "hotels": hotels
    }
    
    logger.log("search_hotels", params, result)
    return result


def check_hotel_availability(
    hotel_id: str,
    check_in: str,
    check_out: str,
    rooms: int = 1
) -> dict[str, Any]:
    """
    Check room availability for a specific hotel.
    
    Args:
        hotel_id: The hotel ID
        check_in: Check-in date
        check_out: Check-out date
        rooms: Number of rooms to check
    
    Returns:
        Dictionary with availability details
    """
    import random
    
    logger = get_logger()
    
    params = {
        "hotel_id": hotel_id,
        "check_in": check_in,
        "check_out": check_out,
        "rooms": rooms
    }
    
    nights = _calculate_nights(check_in, check_out)
    is_available = random.random() > 0.1  # 90% chance available
    
    if is_available:
        available_rooms = []
        for room_type, base_price in [("Standard", 8000), ("Deluxe", 12000), ("Suite", 20000)]:
            qty = random.randint(0, 5)
            if qty > 0:
                available_rooms.append({
                    "room_type": room_type,
                    "available_count": qty,
                    "price_per_night": base_price,
                    "total_price": base_price * nights,
                    "max_occupancy": 2 if room_type == "Standard" else 3,
                    "bed_type": random.choice(["King", "Twin", "Queen"])
                })
        
        result = {
            "success": True,
            "hotel_id": hotel_id,
            "available": True,
            "check_in": check_in,
            "check_out": check_out,
            "nights": nights,
            "rooms_requested": rooms,
            "available_rooms": available_rooms,
            "currency": "INR"
        }
    else:
        result = {
            "success": True,
            "hotel_id": hotel_id,
            "available": False,
            "check_in": check_in,
            "check_out": check_out,
            "message": "No rooms available for selected dates"
        }
    
    logger.log("check_hotel_availability", params, result)
    return result


def book_hotel(
    hotel_offer_id: str,
    guests: list[dict],
    payment_info: dict | None = None,
    dry_run: bool = False
) -> dict[str, Any]:
    """
    Book a hotel reservation.
    
    Args:
        hotel_offer_id: The hotel offer ID to book
        guests: List of guest details
        payment_info: Payment details
        dry_run: If True, simulate without actual booking
    
    Returns:
        Dictionary with booking confirmation or dry-run preview
    """
    logger = get_logger()
    
    params = {
        "hotel_offer_id": hotel_offer_id,
        "guests": guests,
        "payment_info": payment_info,
        "dry_run": dry_run
    }
    
    booking_ref = f"HBK-{uuid.uuid4().hex[:6].upper()}"
    
    if dry_run:
        result = {
            "success": True,
            "status": "DRY_RUN",
            "message": "This is a preview. No actual booking was made.",
            "preview": {
                "booking_reference": booking_ref,
                "hotel_offer_id": hotel_offer_id,
                "guests": len(guests),
                "guest_names": [
                    f"{g.get('first_name', '')} {g.get('last_name', '')}"
                    for g in guests
                ]
            }
        }
    else:
        result = {
            "success": True,
            "status": "CONFIRMED",
            "booking_reference": booking_ref,
            "hotel_offer_id": hotel_offer_id,
            "confirmation_number": f"CONF-{uuid.uuid4().hex[:8].upper()}",
            "guests": [
                {
                    "name": f"{g.get('first_name', '')} {g.get('last_name', '')}",
                    "is_primary": i == 0
                }
                for i, g in enumerate(guests)
            ],
            "special_requests": None,
            "confirmation_email_sent": True,
            "created_at": datetime.now().isoformat()
        }
    
    audit_id = logger.log("book_hotel", params, result)
    result["audit_log_id"] = audit_id
    return result
