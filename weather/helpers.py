import requests
import weather


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


def get_telegram_response(telegram_link):
    """I used it for debugging manually purposes, to actually see the data flow."""
    # "https://api.telegram.org/bot{telegram_key}/getUpdates"
    response = requests.get(telegram_link).json()
    print(response)
