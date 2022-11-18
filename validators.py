import re

# TODO: instead of return false, just raise the exception, less code, no IF ELSE needed in another functions. Up to refactoring.
# TODO: create Validator class?

def validate_sub_type(sub):
    """Validates subscription type input."""
    try:
        return re.search(r"\btoday\b|\bnow\b|\btomorrow\b", sub).group()
    except AttributeError:  # throws attr error when no match found
        return False


def is_time(time):
    """Validates time input (msg_hour)."""
    try:
        return re.search(r"\b(2[0-3]|[01]?[0-9]):([0-5][0-9]):([0-5][0-9])\b", time).group()
    except AttributeError:
        return False


def has_number(string):
    """Checks if user input has digits (used for post code)."""
    return bool(re.search(r"\d", string))


def validate_city(city):
    """Verifies city input. Only a-z letters. For now*"""
    match = re.findall(r"[A-Za-z]+", city)
    if len(match) == 0:     # empty list if no match
        raise Exception(f"{city} is not valid.")
    return " ".join(match)
