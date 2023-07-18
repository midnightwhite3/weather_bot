# openweather_api.py contains functions to work with OPENWEATHER API

import requests
from functools import wraps

import database
import settings


def API_call_counter(fn):
    """Counts API calls made by user. Limit is set, function makes sure that the limit
       cannot be exceeded"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # yet to be improved, but works as expected for now
        try:
            database.API_call_limitter(kwargs['user_id'])
            return fn(*args, **kwargs)
        except database.DBError:
            return "You've reached call's per day limit. Come back tomorrow."
        except Exception as err:
            settings.logger.warning(f'API call counter error - {err}')
    return wrapper


def check_status(fn):
    """Open weather API status checker."""
    @wraps(fn)
    @API_call_counter
    def wrapper1(city, post_code, *args, **kwargs):
        weather_json = forecast_json(city, post_code, *args)
        weather_json.setdefault('message', 'No messsage in response.')
        err_code = str(weather_json['cod']) # status code returned from openweather
        msg = weather_json['message']
        if err_code == '200': return fn(weather_json, post_code, *args, **kwargs)
        try:
            if err_code not in settings.STATUS_CODES:
                settings.STATUS_CODES[err_code] = msg # make it to save new error as file save to keep it after bot restart
        finally:
            cod = [k for k, v in settings.STATUS_CODES.items() if v == settings.STATUS_CODES[err_code]][0]
            settings.logger.warning(f"Status error: {cod} - {msg}")
            # raise StatusError(f"{cod} - {msg}") # get key name not value
    return wrapper1


def forecast_json(city: str, post_code: str, weather_type: str) -> dict:
    """Fetches json response from open weather API, 5 days."""
    json_response = requests.get(f"http://api.openweathermap.org/data/2.5/{weather_type}?q={city},{post_code}&appid={settings.WEATHER_KEY}&units=metric").json()
    return json_response


def weather_now_json(city: str, post_code: str) -> dict:
    """Fetches json response from open weather API, current. !!Out of use for now."""
    json_response = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={city},{post_code}&appid={settings.WEATHER_KEY}&units=metric").json()
    return json_response
