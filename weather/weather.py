import requests
import re
from bs4 import BeautifulSoup

import my_utils
import helpers
import settings
from openweather_api import check_status

# divide this into two separare funcxtions.!!
def find_postal_code(city: str, user_id=None) -> str:
    """Makes post_code arg optional. Scrapes the web for it and returns.
       Post code database saving and retrieving yet to be improved.
       just scrapes the web for post code for now.
    """
    # if is_post_code(user_id) is True:
    #     return get_post_code(user_id)
    my_utils.validate_city(city)
    not_found = f"""Sorry, we couldn't find post code for {city.title()}. Enter it manually.
                Example - 'new york 10001'"""
    try:
        g_url = requests.get(settings.GEONAMES.format(city=city)).text
        soup = BeautifulSoup(g_url, "html.parser")
        pcode_index = [x.text for x in soup.find_all('th')].index('Code')       # find index of post code in table.
        tagged_pcode = soup.find('table', attrs={'class': 'restable'}).findAll('td')
        raw_pcode = re.sub(r'<.*?>', '', str(tagged_pcode[pcode_index]))        # strip post code from html tags.
        if raw_pcode == 'None':     # no post_code, return error msg
            return not_found
        settings.logger.info(f"Post code for {city} found on GEONAMES.ORG")
        # save_post_code(user_id, raw_pcode)
        return raw_pcode        # pcode found, return it
    except ValueError:      # if 'TRY' does not find post code, it raises value error.
        w_url = requests.get(settings.WIKI.format(city=city)).text
        soup = BeautifulSoup(w_url, "html.parser")
        tagged_pcode = soup.find('div', attrs={'class': 'postal-code'})
        raw_pcode = re.sub(r"<.*?>", '', str(tagged_pcode)).split(',')[0]
        if raw_pcode == 'None':
            return not_found
        settings.logger.info(f"Post code for {city} found on WIKIPEDIA.ORG")
        # save_post_code(user_id, raw_pcode)
        return raw_pcode


# TODO: refacor these functions to be more readable.!!!
# ^ divide them to more smaller functions
# ^ ex. assinging data from json response
def weather_message(data: dict, timezone: int) -> str:
    """Converts json response to actual message, readable for the user."""
    try:
        ## assign data ##
        time = data['dt']
        precipitation = data['pop'] if 'pop' in data else 0
        main_data = data['main']
        temp = main_data['temp']
        feels_like = main_data['feels_like']
        pressure = main_data['pressure']
        humidity = main_data['humidity']
        weather_desc = data['weather'][0]['description']
        clouds = data['clouds']['all']
        rain = data['rain'] if 'rain' in data else ''   # chain rain with rain below into one statement
        snow = data['snow'] if 'snow' in data else ''   # same here
        wind_speed = data['wind']['speed']
        wind_gust = data['wind']['gust'] if 'gust' in data['wind'] else None
        if len(rain) > 0: # empty string
            rain = rain['3h'] if '3h' in rain else rain['1h']
        if len(snow) > 0:
            snow = snow['3h'] if '3h' in snow else snow['1h']
        timezone_difference = str(timezone/3600)  # 3600s in hr gets difference between timezones
        
        ## message ##
        msg = f"\n🕗{my_utils.time.strftime('%H:%M', my_utils.time.gmtime(time))} + {timezone_difference}h |" \
            f"☔{round(precipitation*100, 0)}% | 🌡️{round(temp, 1)}°C / {round(feels_like, 1)}C°\n" \
            f"Pressure: {pressure}hPa | Humidity: {humidity}%\n" \
            f"{weather_desc} | ☁️{clouds}% | {helpers.get_wind_direction(data)}\n" \
            f"Wind: {round(my_utils.mps_to_kmh(wind_speed), 2)}km/h"
        if wind_gust is not None:
            msg += f" | Gusting: {round(my_utils.mps_to_kmh(wind_gust))}km/h\n"
        else: msg += '\n'
        return msg
    except Exception:       # unexpected errors catch, to not return an errors msg to the user on telegram
        settings.logger.warning("Unknown error.", exc_info=True)
        return "Something is wrong, try again later." # Raise instead?


@check_status
def weather(response: dict, *args, **kwargs):
    post_code = args[0]
    country = helpers.get_country(response)
    weather = response['list']
    timezone = int(response['city']['timezone'])
    sunrise, sunset = response['city']['sunrise'], response['city']['sunset']

    msg = f"{country} | {post_code}"
    for item in weather:
        date = item['dt_txt'][:10]
        if date == str(kwargs['day']()):    # day is a function specified in kwargs
            msg += weather_message(item, timezone)
    msg += f"\n☀️{my_utils.time.strftime('%H:%M', my_utils.time.gmtime(sunrise + timezone))}  " \
           f"🌑{my_utils.time.strftime('%H:%M', my_utils.time.gmtime(sunset + timezone))}"
    return msg


@check_status
def weather_now(response: dict, *args, **kwargs) -> str:
    """Makes an API call and returns weather for now via 'weather_message' and adds sunset/sunrise text
       to the message.
    """
    post_code = args[0]
    country = helpers.get_country(response)
    timezone = int(response['timezone'])
    sunrise, sunset = response['sys']['sunrise'], response['sys']['sunset']
    msg = f"{country} | {post_code} {weather_message(response, timezone)}"
    msg += f"\n☀️{my_utils.time.strftime('%H:%M', my_utils.time.gmtime(sunrise + timezone))}  " \
           f"🌑{my_utils.time.strftime('%H:%M', my_utils.time.gmtime(sunset + timezone))}"
    return msg
