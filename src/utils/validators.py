"""
Input validation utilities for Travel Agent.
Validates dates, IATA codes, currencies, and other travel-specific inputs.
"""

import re
from datetime import datetime
from typing import Tuple


# Valid IATA airport codes (sample set - in production would be a complete list)
VALID_IATA_CODES = {
    "MAA", "SIN", "BOM", "DEL", "BLR", "HYD", "CCU", "PNQ", "COK", "GOI",  # India
    "DXB", "DOH", "AUH", "BAH", "KWI", "MCT", "RUH", "JED",  # Middle East
    "LHR", "CDG", "FRA", "AMS", "FCO", "BCN", "MAD", "MUC", "ZRH", "VIE",  # Europe
    "JFK", "LAX", "SFO", "ORD", "MIA", "BOS", "SEA", "ATL", "DFW", "DEN",  # USA
    "HKG", "NRT", "ICN", "BKK", "KUL", "CGK", "MNL", "SGN", "HAN", "PEK",  # Asia
    "SYD", "MEL", "AKL", "PER", "BNE",  # Oceania
}

# Valid currency codes
VALID_CURRENCIES = {"INR", "USD", "EUR", "GBP", "SGD", "AED", "JPY", "AUD", "THB", "MYR"}

# Valid cabin classes
VALID_CABIN_CLASSES = {"ECONOMY", "PREMIUM_ECONOMY", "BUSINESS", "FIRST"}


def validate_date(date_string: str) -> Tuple[bool, str]:
    """
    Validate ISO-8601 date format (YYYY-MM-DD).
    
    Returns:
        Tuple of (is_valid, error_message_or_date)
    """
    try:
        parsed_date = datetime.strptime(date_string, "%Y-%m-%d")
        if parsed_date.date() < datetime.now().date():
            return False, f"Date {date_string} is in the past"
        return True, date_string
    except ValueError:
        return False, f"Invalid date format: {date_string}. Expected YYYY-MM-DD (ISO-8601)"


def validate_iata_code(code: str) -> Tuple[bool, str]:
    """
    Validate IATA airport code (3 uppercase letters).
    
    Returns:
        Tuple of (is_valid, error_message_or_code)
    """
    code = code.upper().strip()
    if not re.match(r"^[A-Z]{3}$", code):
        return False, f"Invalid IATA code format: {code}. Expected 3 letters."
    if code not in VALID_IATA_CODES:
        # Allow unknown codes but warn (could be valid codes we don't have)
        return True, code  # Accept it anyway for flexibility
    return True, code


def validate_currency(currency: str) -> Tuple[bool, str]:
    """
    Validate currency code (3 uppercase letters).
    
    Returns:
        Tuple of (is_valid, error_message_or_currency)
    """
    currency = currency.upper().strip()
    if currency not in VALID_CURRENCIES:
        return False, f"Unsupported currency: {currency}. Supported: {', '.join(sorted(VALID_CURRENCIES))}"
    return True, currency


def validate_passenger_count(count: int) -> Tuple[bool, str]:
    """
    Validate passenger count (1-9 per booking).
    
    Returns:
        Tuple of (is_valid, error_message_or_count)
    """
    if not isinstance(count, int) or count < 1 or count > 9:
        return False, f"Invalid passenger count: {count}. Must be 1-9."
    return True, str(count)


def validate_cabin_class(cabin_class: str) -> Tuple[bool, str]:
    """
    Validate cabin class.
    
    Returns:
        Tuple of (is_valid, error_message_or_class)
    """
    cabin_class = cabin_class.upper().strip()
    if cabin_class not in VALID_CABIN_CLASSES:
        return False, f"Invalid cabin class: {cabin_class}. Valid: {', '.join(VALID_CABIN_CLASSES)}"
    return True, cabin_class
