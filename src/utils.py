import re


def extract_four_digits(string: str = "1234") -> str:
    """
    Returns the first group of four consecutive numbers matched in the
    string.
    """
    # four consecutive numbers - group match
    pattern = re.compile(r"\b(\d{4})\b")
    match = pattern.search(string)
    if match:
        result = match.group(1)
    else:
        result = string
    return str(result)
