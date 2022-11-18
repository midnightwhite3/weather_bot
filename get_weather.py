from bs4 import BeautifulSoup
import requests
from datetime import datetime
from time import gmtime, strftime, time
from settings import telegram_key, weather_key, logger
import re
from validators import validate_city

# TODO: merge weather_now and weather_tomorrow functions?
# TODO: divide find_postal_code func in two? each function for each site? a Class perhaps?
# TODO: divide weather_message to more smaller functions?


class StatusError(Exception): pass


today = datetime.today().date()
tomorrow = strftime("%Y-%m-%d", gmtime(time() + 86400))


def find_postal_code(city):
    """Makes post_code arg optional. Scrapes the web for it and returns."""
    validate_city(city)
    not_found = f"""Sorry, we couldn't find post code for {city.title()}. Enter it manually.
                Example - 'new york 10001'"""
    try:
        g_url = requests.get(f"https://www.geonames.org/postalcode-search.html?q={city}&country=").text
        soup = BeautifulSoup(g_url, "html.parser")
        pcode_index = [x.text for x in soup.find_all('th')].index('Code')       # find index of post code in table.
        tagged_pcode = soup.find('table', attrs={'class': 'restable'}).findAll('td')
        raw_pcode = re.sub(r'<.*?>', '', str(tagged_pcode[pcode_index]))        # strip post code from html tags.
        if raw_pcode == 'None':     # no post_code, return error msg
            return not_found
        logger.info("Post code found on GEONAMES.ORG")
        return raw_pcode        # pcode found, return it
    except ValueError:      # if 'TRY' does not find post code, it raises value error.
        w_url = requests.get(f"https://en.wikipedia.org/wiki/{city}").text
        soup = BeautifulSoup(w_url, "html.parser")
        tagged_pcode = soup.find('div', attrs={'class': 'postal-code'})
        raw_pcode = re.sub(r"<.*?>", '', str(tagged_pcode))
        if raw_pcode == 'None':
            return not_found
        logger.info("Post code found on WIKIPEDIA.ORG")
        return raw_pcode
 

def get_forecast_json(city, post_code):
    """Fetches json response from open weather API, 5 days."""
    json_response = requests.get(f"http://api.openweathermap.org/data/2.5/forecast?q={city},{post_code}&appid={weather_key}&units=metric").json()
    return json_response


def get_weather_now_json(city, post_code):
    """Fetches json response from open weather API, current."""
    json_response = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={city},{post_code}&appid={weather_key}&units=metric").json()
    return json_response


def get_country(data):
    try:
        if 'sys' in data: msg = f"Country: {data['sys']['country']}\n"
        elif 'city' in data: msg = f"Country: {data['city']['country']}\n"
        return msg
    except Exception:
        logger.error("Exception occured.", exc_info=True)
        pass


def check_status(json_response):
    err_cod = str(json_response['cod']) # status code returned from openweather
    msg = "No message in response."
    if  'message' in json_response:      # openweather API not always returns this in response, KEY error solution
        msg = json_response['message']
    if err_cod == '404':                # 404 code means no city with that post code in DB
        logger.exception(msg, exc_info=True)   # log it
        raise StatusError("City not found.")
    elif err_cod == '429':              # im using free plan so i have call limit, 429 is a code for that error
        logger.warning(msg, exc_info=True)
        raise StatusError("I've reached the limit of server calls for now. Try again later or come back tomorrow.")
    elif err_cod != '200':      # other errors not specified by openweather, status 200 is SUCCESS
        logger.error(msg=(msg, err_cod), exc_info=True)
        raise StatusError("Something is wrong on the server side. Try again later since I'm trying to fix this ASAP.")
    else: pass  # no errors, pass it


def weather_message(data, timezone):
    """Converts json response to actual message, readable for the user."""
    try:
        msg = f"\n🕗{strftime('%H:%M', gmtime(data['dt']))} + {str(int(timezone/3600))}h | "    # 3600s in hr gets difference between timezones
        if 'pop' in data:                               # rain probability
            pop = data['pop']
        else: pop = 0
        msg += f"☔{round(pop*100, 0)}% | "
        msg += f"🌡️{round(data['main']['temp'], 1)}\N{DEGREE SIGN}C / {round(data['main']['feels_like'], 1)}" \
               f"\N{DEGREE SIGN}C\n" \
               f"Pressure: {data['main']['pressure']}hPa | Humidity: {data['main']['humidity']}%\n" \
               f"{data['weather'][0]['description']} | ☁️{data['clouds']['all']}% | {get_wind_direction(data)}"

        # check if is raining, if it is check if it has 1 or 3 hour rain count 
        if 'rain'in data:
            if '3h' in data['rain']:                # open weather API says that it returns 3h and 1h
                msg += f"\n💧{data['rain']['3h']}mm"    # sometimes its just one, depending on now or forecast
            else:
                msg += f"\n💧{data['rain']['1h']}mm"

        # same as rain above
        if 'snow' in data:
            if '3h' in data['snow']:
                msg += f"\n❄️{data['snow']['3h']}mm"
            else:
                msg += f"\n❄️{data['snow']['1h']}mm"

        msg += f"\n🌬️{round(data['wind']['speed']*3.6, 2)}km/h"     # *3.6 to convert from meters/s.
        if 'gust' in data['wind']:      # there is no gust sometimes in json_response
            msg += f" | Gusting: {round(data['wind']['gust']*3.6, 2)}km/h\n"
        return msg
    except Exception:       # unexpected errors catch, to not return an errors msg to the user on telegram
        logger.exception("Unknown error.", exc_info=True)
        return "Something is wrong, try again later."
    

def weather_today(city, post_code):
    """Open weather API call is for 5 days, function returns weather for the current day via 'weather_message'
       and adds sunrise/sunset text to the message."""
    weather_json = get_forecast_json(city=city, post_code=post_code)
    check_status(weather_json)
    msg = get_country(weather_json)
    timezone = int(weather_json['city']['timezone'])
    sunrise, sunset = weather_json['city']['sunrise'], weather_json['city']['sunset']
    for item in weather_json['list']:
        if item['dt_txt'][:10] == str(today):
            msg += weather_message(item, timezone)
    msg += f"\n☀️{strftime('%H:%M', gmtime(sunrise + timezone))}  " \
           f"🌑{strftime('%H:%M', gmtime(sunset + timezone))}"
    return msg


def weather_now(city, post_code):
    """Makes an API call and returns weather for now via 'weather_message' and adds sunset/sunrise text
       to the message."""
    weather_json = get_weather_now_json(city, post_code)
    check_status(weather_json)
    msg = get_country(weather_json)
    timezone = int(weather_json['timezone'])
    sunrise, sunset = weather_json['sys']['sunrise'], weather_json['sys']['sunset']
    msg += weather_message(weather_json, timezone)
    msg += f"\n☀️{strftime('%H:%M', gmtime(sunrise + timezone))}  " \
           f"🌑{strftime('%H:%M', gmtime(sunset + timezone))}"
    return msg


def weather_tomorrow(city, post_code):
    """Look, weather_today -> but for tomorrow."""
    weather_json = get_forecast_json(city=city, post_code=post_code)
    check_status(weather_json)
    msg = get_country(weather_json)
    timezone = int(weather_json['city']['timezone'])
    sunrise, sunset = weather_json['city']['sunrise'], weather_json['city']['sunset']
    for item in weather_json['list']:
        if item['dt_txt'][:10] == str(tomorrow):    # forecats is for 5 days, check only for tomorrow.
            msg += weather_message(item, timezone)
    msg += f"\n☀️{strftime('%H:%M', gmtime(sunrise + timezone))}  " \
           f"🌑{strftime('%H:%M', gmtime(sunset + timezone))}"
    return msg


def get_wind_direction(degree):
    """Fetches wind directions in degrees and changes it to one of 8 directions of the world."""
    wind_deg = degree['wind']['deg']
    directions = ['⬆️N', '↗️NE', '➡️E', '↘️SE', '⬇️S', '↙️SW', '⬅️W', '↖️NW']
    degrees = int((wind_deg/45)+.5)
    return directions[(degrees % 8)]    # modulo still kind of mystery for me, list wrapper.


def get_telegram_reponse():
    """I used it for debugging manually purposes, to actually see the data flow."""
    response = requests.get(f"https://api.telegram.org/bot{telegram_key}/getUpdates").json()
    print(response)
