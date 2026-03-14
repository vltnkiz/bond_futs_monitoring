from datetime import datetime


def convert_contract_symbol(raw_contract: str) -> str:
    """
    Example: "CONF 2026-03-06" -> "CONFH26"
    """
    month_codes = {
        1: 'F', 2: 'G', 3: 'H', 4: 'J', 5: 'K', 6: 'M',
        7: 'N', 8: 'Q', 9: 'U', 10: 'V', 11: 'X', 12: 'Z'
    }
    
    # Parse "CONF 2026-03-06" format
    parts = raw_contract.split()
    if len(parts) == 2:
        product_code = parts[0]
        date_str = parts[1]
        
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
            month_letter = month_codes[date.month]
            year_2digit = date.strftime("%y")
            return f"{product_code}{month_letter}{year_2digit}"
        except (ValueError, KeyError):
            # If parsing fails, return original
            return raw_contract
    
    return raw_contract