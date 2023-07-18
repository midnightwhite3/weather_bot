import re

import my_utils


def validate_city(city: str) -> str: #change it to boolean return?
    """Verifies city input. Only a-z letters. For now*.
    Exception is raised if no match found.
    """
    match = re.findall(r"[A-Za-z]+", city)
    if len(match) == 0:     # empty list if no match
        raise Exception(f"{city} is not valid.")
    return " ".join(match)


def validate_sub_type(sub: str):
    """Validates subscription type input."""
    try:
        return re.search(r"\btoday\b|\bnow\b|\btomorrow\b", sub).group()
    except AttributeError:  # throws attr error when no match found
        return False


def is_hour_greater(subscribers: list) -> list:
    """Returns list of subscribers with subbed_hour greater than current hour."""
    subs = [sub for sub in subscribers if sub[2] >= my_utils.hour_now_str]
    return subs


def has_number(string: str) -> bool:
    """Checks if user input has digits (used for post code)."""
    return bool(re.search(r"\d", string))


def is_time(time: str):
    """Validates time input (msg_hour)."""
    try:
        return re.search(r"\b(2[0-3]|[01]?[0-9]):([0-5][0-9]):([0-5][0-9])\b", time).group()
    except AttributeError:
        return False
