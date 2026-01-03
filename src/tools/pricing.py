"""
Pricing and cost estimation tools.
Calculates total trip costs including flights, hotels, and additional expenses.
"""

import uuid
from typing import Any

from ..utils.logger import get_logger


def estimate_total_cost(
    flight_price: float,
    hotel_price: float,
    currency: str,
    include_taxes: bool = True,
    additional_costs: dict[str, float] | None = None
) -> dict[str, Any]:
    """
    Calculate the total estimated cost for a trip.
    
    Args:
        flight_price: Total flight cost
        hotel_price: Total hotel cost
        currency: Currency code
        include_taxes: Whether prices already include taxes
        additional_costs: Any additional costs (transfers, activities, etc.)
    
    Returns:
        Dictionary with cost breakdown
    """
    logger = get_logger()
    
    params = {
        "flight_price": flight_price,
        "hotel_price": hotel_price,
        "currency": currency,
        "include_taxes": include_taxes,
        "additional_costs": additional_costs
    }
    
    # Calculate base totals
    subtotal = flight_price + hotel_price
    
    # Process additional costs
    additional_total = 0
    additional_breakdown = {}
    if additional_costs:
        for name, amount in additional_costs.items():
            additional_breakdown[name] = amount
            additional_total += amount
    
    # Calculate taxes if not included
    estimated_taxes = 0
    if not include_taxes:
        estimated_taxes = subtotal * 0.12  # 12% estimated tax
    
    # Service fee
    service_fee = subtotal * 0.02  # 2% service fee
    
    grand_total = subtotal + additional_total + estimated_taxes + service_fee
    
    result = {
        "success": True,
        "estimate_id": f"EST-{uuid.uuid4().hex[:8].upper()}",
        "breakdown": {
            "flights": {
                "amount": flight_price,
                "currency": currency
            },
            "hotels": {
                "amount": hotel_price,
                "currency": currency
            },
            "additional": additional_breakdown if additional_breakdown else None,
            "additional_total": additional_total if additional_total > 0 else None
        },
        "subtotal": round(subtotal, 2),
        "taxes_included": include_taxes,
        "estimated_taxes": round(estimated_taxes, 2) if not include_taxes else 0,
        "service_fee": round(service_fee, 2),
        "grand_total": round(grand_total, 2),
        "currency": currency,
        "disclaimer": "This is an estimate. Final prices may vary based on availability and exchange rates."
    }
    
    logger.log("estimate_total_cost", params, result)
    return result
