"""
FlightAPI.io client for real flight search.
Provides real-time flight price data from multiple vendors.
"""

import os
import requests
from typing import Any, Optional

from ..utils.logger import get_logger


FLIGHTAPI_BASE_URL = "https://api.flightapi.io"


def _get_api_key() -> str:
    """Get FlightAPI key from environment."""
    key = os.getenv("FLIGHT_API")
    if not key:
        raise ValueError("FLIGHT_API not set. Get your API key at https://www.flightapi.io")
    return key


def search_flights_real(
    origin: str,
    destination: str,
    departure_date: str,
    adults: int = 1,
    children: int = 0,
    infants: int = 0,
    cabin_class: str = "Economy",
    currency: str = "INR",
    return_date: Optional[str] = None
) -> dict[str, Any]:
    """
    Search for flights using FlightAPI.io.
    
    Args:
        origin: Origin airport IATA code (e.g., "MAA")
        destination: Destination airport IATA code (e.g., "SIN")
        departure_date: Departure date (YYYY-MM-DD)
        adults: Number of adult passengers
        children: Number of children
        infants: Number of infants
        cabin_class: Cabin class (Economy, Business, First, Premium_Economy)
        currency: Currency code (INR, USD, etc.)
        return_date: Optional return date for round trips
    
    Returns:
        Dictionary with flight search results
    """
    logger = get_logger()
    
    params = {
        "origin": origin,
        "destination": destination,
        "departure_date": departure_date,
        "adults": adults,
        "children": children,
        "infants": infants,
        "cabin_class": cabin_class,
        "currency": currency
    }
    
    try:
        api_key = _get_api_key()
        
        # Build the API URL based on trip type
        if return_date:
            # Round trip
            url = f"{FLIGHTAPI_BASE_URL}/roundtrip/{api_key}/{origin}/{destination}/{departure_date}/{return_date}/{adults}/{children}/{infants}/{cabin_class}/{currency}"
        else:
            # One-way trip
            url = f"{FLIGHTAPI_BASE_URL}/onewaytrip/{api_key}/{origin}/{destination}/{departure_date}/{adults}/{children}/{infants}/{cabin_class}/{currency}"
        
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        
        data = response.json()
        
        # Parse the response
        itineraries = data.get("itineraries", [])
        legs = {leg.get("id"): leg for leg in data.get("legs", [])}
        segments = {seg.get("id"): seg for seg in data.get("segments", [])}
        carriers = {str(c.get("id")): c for c in data.get("carriers", [])}
        places = {str(p.get("id")): p for p in data.get("places", [])}
        
        flights = []
        for itin in itineraries[:15]:  # Limit to 15 results
            pricing_options = itin.get("pricing_options", [])
            if not pricing_options:
                continue
            
            best_price = pricing_options[0].get("price", {})
            leg_ids = itin.get("leg_ids", [])
            
            # Get leg details
            flight_legs = []
            total_duration = 0
            stops = 0
            
            for leg_id in leg_ids:
                leg = legs.get(leg_id, {})
                if leg:
                    total_duration += leg.get("duration", 0)
                    stops += leg.get("stop_count", 0)
                    
                    # Get carrier info
                    carrier_ids = leg.get("marketing_carrier_ids", [])
                    carrier_name = "Unknown"
                    carrier_code = ""
                    if carrier_ids:
                        carrier = carriers.get(str(carrier_ids[0]), {})
                        carrier_name = carrier.get("name", "Unknown")
                        carrier_code = carrier.get("iata", "")
                    
                    # Get place names
                    origin_place = places.get(str(leg.get("origin_place_id")), {})
                    dest_place = places.get(str(leg.get("destination_place_id")), {})
                    
                    flight_legs.append({
                        "departure": leg.get("departure"),
                        "arrival": leg.get("arrival"),
                        "duration_minutes": leg.get("duration", 0),
                        "stops": leg.get("stop_count", 0),
                        "origin": origin_place.get("iata", origin),
                        "destination": dest_place.get("iata", destination),
                        "carrier": {
                            "name": carrier_name,
                            "code": carrier_code
                        }
                    })
            
            # Get the primary carrier
            primary_carrier = flight_legs[0]["carrier"] if flight_legs else {"name": "Unknown", "code": ""}
            
            flight = {
                "offer_id": itin.get("id", ""),
                "airline": primary_carrier,
                "price": {
                    "amount": best_price.get("amount", 0),
                    "currency": currency,
                    "total": best_price.get("amount", 0)
                },
                "legs": flight_legs,
                "total_duration_minutes": total_duration,
                "stops": stops,
                "cabin_class": cabin_class,
                "booking_url": pricing_options[0].get("items", [{}])[0].get("url", "") if pricing_options else ""
            }
            flights.append(flight)
        
        # Sort by price
        flights.sort(key=lambda x: x["price"]["amount"])
        
        result = {
            "success": True,
            "source": "flightapi.io",
            "query": params,
            "results_count": len(flights),
            "flights": flights
        }
        
        logger.log("search_flights_real", params, {"success": True, "count": len(flights)})
        return result
        
    except requests.exceptions.RequestException as e:
        error_result = {
            "success": False,
            "error": f"API request failed: {str(e)}",
            "source": "flightapi.io"
        }
        logger.log("search_flights_real", params, error_result, success=False, error=str(e))
        return error_result
    except ValueError as e:
        error_result = {
            "success": False,
            "error": str(e),
            "source": "flightapi.io"
        }
        logger.log("search_flights_real", params, error_result, success=False, error=str(e))
        return error_result
    except Exception as e:
        error_result = {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "source": "flightapi.io"
        }
        logger.log("search_flights_real", params, error_result, success=False, error=str(e))
        return error_result
