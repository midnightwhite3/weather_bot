import requests
import weather
import settings

import re
from bs4 import BeautifulSoup


def get_wind_direction(degree) -> str:
    """Fetches wind directions in degrees and changes it to one of 8 directions of the world."""
    wind_deg = degree['wind']['deg']
    directions = ['⬆️N', '↗️NE', '➡️E', '↘️SE', '⬇️S', '↙️SW', '⬅️W', '↖️NW']
    degrees = int((wind_deg/45)+.5)
    return directions[(degrees % 8)]    # modulo list wrapper.


def get_country(data: dict) -> str:
    try:
        country = data['sys']['country'] if 'sys' in data else data['city']['country']
        # "Country: {data['sys']['country']}\n"
        return country
    except Exception: # cant remember why i put exception here, check OW response
        weather.settings.logger.exception("Exception occured.", exc_info=True)
        pass


def get_telegram_response(telegram_link: str):
    """I used it for debugging manually purposes, to actually see the data flow."""
    # "https://api.telegram.org/bot{telegram_key}/getUpdates"
    response = requests.get(telegram_link).json()
    print(response)


def geonames_find_pcode(city: str, site_name="GEONAMES.ORG", site_url=settings.GEONAMES_URL):
    """Looks for post code on GEONAMES and returns it raw."""
    soup = make_soup(site_url, city)
    pcode_index = [x.text for x in soup.find_all('th')].index('Code')       # find index of post code in table.
    tagged_pcode = soup.find('table', attrs={'class': 'restable'}).findAll('td')
    raw_pcode = re.sub(r'<.*?>', '', str(tagged_pcode[pcode_index]))        # strip post code from html tags.
    return pcode_log_and_return(city, raw_pcode, site_name)


def wikipedia_find_pcode(city: str, site_name="WIKIPEDIA.ORG", site_url=settings.WIKI_URL):
    """Looks for post code on GEONAMES and returns it raw."""
    soup = make_soup(site_url, city)
    tagged_pcode = soup.find('div', attrs={'class': 'postal-code'})
    raw_pcode = re.sub(r"<.*?>", '', str(tagged_pcode)).split(',')[0]
    return pcode_log_and_return(city, raw_pcode, site_name)


def make_soup(url: str, city: str):
    url_text = requests.get(url.format(city=city)).text
    return BeautifulSoup(url_text, "html.parser")


def pcode_log_and_return(city: str, raw_pcode: str, site_name: str):
    """Verifies if post code was found. Returns error msg to user or 
    valid post code as string. Logs the output."""
    if raw_pcode == 'None':
        settings.logger.info("Post code not found.")
        return settings.pcode_not_found.format(city=city)
    settings.logger.info(settings.pcode_found.format(city=city, site=site_name))
    return raw_pcode


def parse_ow_data():
    pass
