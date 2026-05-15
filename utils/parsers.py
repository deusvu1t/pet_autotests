def parse_price(text: str) -> float:
    return float(text.replace("$", ""))
