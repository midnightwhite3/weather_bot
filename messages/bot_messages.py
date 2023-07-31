# bot_messages.py

BOT_MSGS = {
    'help': """I can show you the weather for any city in the world u ask!
    In order to do that, you must use one of the commands:
    -/today - weather for today with 3hour timestamps
    -/tomorrow - weather for tomorrow with 3hour timestamps
    -/now - weather for now
    After the command, I need you to type a city name and a post code (optional).
    If you don't know the post code for the city, it's ok, I will try to search it automatically.
    When i find it, i'm gonna send you the forecast.
    When I don't, well, you will have to provide one for me, sorry.
    Example:
    /now california
    Example output:
    New York 10001 | Country: US
    🕗09:53 + -4h | 🌡️11.4°C / 10.7°C
    Pressure: 1018hPa | Humidity: 81%
    overcast clouds | ☁️99% | ⬅️W
    🌬️1.62km/h | Gusting: 3.2km/h
    ☀️07:25  🌑17:54
    Informations in order:
    - Hour UTC 0 + city timezone gives you city time
    - Temperature and feels like temperature
    - Rain probability
    - Pressure
    - Humidity
    - Main weather description
    - Cloudiness in %
    - Wind direction
    - Rain or snow volume
    - Wind speed | wind speed in gusts
    - Time of sunrise and sunset
    """,


}