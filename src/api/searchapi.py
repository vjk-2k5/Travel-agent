"""
SearchAPI.io client for Google Hotels search.
Provides real hotel search data using SearchAPI's Google Hotels API.
"""

import os
import requests
from typing import Any, Optional

from ..utils.logger import get_logger


SEARCHAPI_BASE_URL = "https://www.searchapi.io/api/v1/search"


def _get_api_key() -> str:
    """Get SearchAPI key from environment."""
    key = os.getenv("SEARCH_API") or os.getenv("SEARCHAPI_KEY")
    if not key:
        raise ValueError("SEARCH_API not set. Get your API key at https://www.searchapi.io")
    return key


def search_hotels_real(
    location: str,
    check_in: str,
    check_out: str,
    adults: int = 2,
    rooms: int = 1,
    hotel_class: Optional[int] = None,
    currency: str = "USD",
    language: str = "en"
) -> dict[str, Any]:
    """
    Search for hotels using SearchAPI's Google Hotels API.
    
    Args:
        location: Location to search (e.g., "Hotels in Singapore" or "Marina Bay Singapore")
        check_in: Check-in date (YYYY-MM-DD)
        check_out: Check-out date (YYYY-MM-DD)
        adults: Number of adult guests
        rooms: Number of rooms
        hotel_class: Filter by star rating (1-5)
        currency: Currency code for pricing
        language: Language code
    
    Returns:
        Dictionary with hotel search results
    """
    logger = get_logger()
    
    params = {
        "engine": "google_hotels",
        "q": f"Hotels in {location}" if not location.lower().startswith("hotels") else location,
        "check_in_date": check_in,
        "check_out_date": check_out,
        "adults": str(adults),
        "currency": currency,
        "hl": language,
        "gl": "us"  # Google location
    }
    
    if hotel_class:
        params["hotel_class"] = str(hotel_class)
    
    try:
        api_key = _get_api_key()
        params["api_key"] = api_key
        
        response = requests.get(SEARCHAPI_BASE_URL, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # Transform response to our format
        properties = data.get("properties", [])
        hotels = []
        
        for prop in properties[:10]:  # Limit to 10 results
            hotel = {
                "hotel_id": prop.get("property_token", ""),
                "name": prop.get("name", "Unknown Hotel"),
                "description": prop.get("description", ""),
                "rating": prop.get("rating", 0),
                "reviews": prop.get("reviews", 0),
                "hotel_class": prop.get("extracted_hotel_class", 0),
                "location": {
                    "city": prop.get("city", ""),
                    "country": prop.get("country", ""),
                    "coordinates": prop.get("gps_coordinates", {})
                },
                "check_in_time": prop.get("check_in_time", ""),
                "check_out_time": prop.get("check_out_time", ""),
                "price": {
                    "per_night": prop.get("price_per_night", {}).get("extracted_price", 0),
                    "total": prop.get("total_price", {}).get("extracted_price", 0),
                    "currency": currency
                },
                "amenities": prop.get("amenities", []),
                "images": [img.get("thumbnail") for img in prop.get("images", [])[:3]],
                "deal": prop.get("deal", None),
                "nearby_places": [
                    {
                        "name": place.get("name", ""),
                        "distance": place.get("transportations", [{}])[0].get("duration", "")
                    }
                    for place in prop.get("nearby_places", [])[:3]
                ]
            }
            hotels.append(hotel)
        
        result = {
            "success": True,
            "source": "searchapi.io",
            "query": {
                "location": location,
                "check_in": check_in,
                "check_out": check_out,
                "adults": adults
            },
            "total_results": data.get("search_information", {}).get("total_results", len(hotels)),
            "results_count": len(hotels),
            "hotels": hotels
        }
        
        logger.log("search_hotels_real", params, {"success": True, "count": len(hotels)})
        return result
        
    except requests.exceptions.RequestException as e:
        error_result = {
            "success": False,
            "error": f"API request failed: {str(e)}",
            "source": "searchapi.io"
        }
        logger.log("search_hotels_real", params, error_result, success=False, error=str(e))
        return error_result
    except ValueError as e:
        error_result = {
            "success": False,
            "error": str(e),
            "source": "searchapi.io"
        }
        logger.log("search_hotels_real", params, error_result, success=False, error=str(e))
        return error_result
