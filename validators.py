import re

# TODO: instead of return false, just raise the exception, less code, no IF ELSE needed in another functions. Up to refactoring.
# TODO: create Validator class?
# TODO: replace has number with validate city func?

def validate_sub_type(sub):
    try:
        return re.search(r"\btoday\b|\bnow\b|\btomorrow\b", sub).group()
    except AttributeError:  # throws attr error when no match found
        return False


def is_time(time):
    try:
        return re.search(r"\b(2[0-3]|[01]?[0-9]):([0-5][0-9]):([0-5][0-9])\b", time).group()
    except AttributeError:
        return False


def has_number(string):
    return bool(re.search(r"\d", string))


def validate_city(city):
    try:
        return re.search(r"([A-Za-z]+ *)*", city).group()
    except AttributeError:
        raise Exception(f"{city} is not valid")

print(validate_city('fgfg 56'))  #wrogn func, doesnt do what intended
