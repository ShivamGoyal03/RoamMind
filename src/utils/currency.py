from typing import Union, Optional
from decimal import Decimal, ROUND_HALF_UP

def format_price(
    amount: Union[float, Decimal],
    currency: str = "USD",
    locale: str = "en_US"
) -> str:
    """Format price with currency symbol."""
    if currency == "USD":
        return f"${amount:,.2f}"
    elif currency == "EUR":
        return f"€{amount:,.2f}"
    elif currency == "GBP":
        return f"£{amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"

def parse_price(price_str: str) -> Optional[float]:
    """Parse price string to float."""
    try:
        # Remove currency symbols and whitespace
        cleaned = price_str.replace("$", "").replace("€", "").replace("£", "").strip()
        # Remove thousands separators and convert to float
        return float(cleaned.replace(",", ""))
    except ValueError:
        return None

def convert_currency(
    amount: float,
    from_currency: str,
    to_currency: str,
    rates: dict
) -> Optional[float]:
    """Convert amount between currencies using provided rates."""
    try:
        if from_currency == to_currency:
            return amount
            
        if from_currency not in rates or to_currency not in rates:
            return None
            
        # Convert to USD first (assuming rates are against USD)
        usd_amount = amount / rates[from_currency]
        # Convert from USD to target currency
        converted = usd_amount * rates[to_currency]
        
        # Round to 2 decimal places
        decimal_amount = Decimal(str(converted))
        rounded = decimal_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        return float(rounded)
    except Exception:
        return None 