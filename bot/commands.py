# commands.py

import weather
import my_utils
import database
from settings import SUB_TYPE, logger
from main import db_change_event


def today_weather_command(update, context):
    """Today weather command."""
    weather_msg_conditional(update, context, weather.weather, weather_type='forecast', day=my_utils.today_date)


def tomorrow_weather_command(update, context):
    """Tomorrow weather command."""
    weather_msg_conditional(update, context, weather.weather, weather_type='forecast', day=my_utils.tomorrow_str)


def now_weather_command(update, context):
    """Now weather command."""
    weather_msg_conditional(update, context, weather.weather_now, weather_type='weather')


def save_city_command(update, context):
    """After simple validation stores city for user_id. If user does not exist, storing user first then city."""
    try:
        city = ' '.join(context.args)
        my_utils.validate_city(city)
        user_name = update.message.from_user.name
        user_id = update.message.from_user.id
        if not database.user_exists(user_id):
            database.store_user(user_id, user_name)
        database.store_location(user_id, city)
        db_change_event.set()
        update.message.reply_text(f"{city.title()} has been saved successfully!")
        logger.info(f"{city.title()} for user {user_id} has been updated.")
    except:
        update.message.reply_text(traceback.print_exc())
        logger.error(traceback.print_exc())


def subscribe_command(update, context):
    """Allows to subscribe for daily weather messages."""
    user_id = update.message.from_user.id
    subbed = my_utils.validate_sub_type(' '.join(context.args))      # if user didnt type sub type, returns False
    hour = my_utils.is_time(' '.join(context.args))
    msg = ""
    if type(subbed) == bool:    # validate sub returns bool (FALSE) if sub type is not given
        update.message.reply_text(f"""You must specify subscription type.\nOptions are - tomorrow, today, now.\nExample:
        /sub new york today 08:00:00""")
        return
    sub = SUB_TYPE[my_utils.validate_sub_type(' '.join(context.args))]    # user typed sub type, use dict to convert it to numeric
    if type(hour) == str and type(subbed) == str:      # if it's string, hour and sub type is given
        city = " ".join(context.args[:-2])
    elif type(subbed) == str and len(context.args[:-1]) > 1:
        city = " ".join(context.args[:-1])
    else:
        city = context.args[0]
    if type(hour) == bool:  # user didnt give the hour so we set the default
        hour = '06:00:00'
        msg += (f"""You didn't specify hour or gave wrong format so I set it to be 06:00:00.\nTo change that, use '/set_hour HH:MM:SS'.\n""")
    my_utils.validate_city(city)
    database.subscribe(user_id, sub, hour, city)
    db_change_event.set()
    update.message.reply_text(msg + f"Subbed successfully. You will receive weather for {city.title()} at {hour} everyday.")
    logger.info(f"SUB - user: {user_id} | subbed for: {sub} | city: {city.title()} | hour: {hour}")


def set_msg_hour_command(update, context):
    """Allows to change hour for weather messages."""
    user_id = update.message.from_user.id
    msg_hour = my_utils.is_time(' '.join(context.args))
    if not msg_hour:
        update.message.reply_text(f"""{msg_hour} is not valid. Make sure you use 24hr format. Example:\n06:00:00""")
        return
    try:
        database.set_msg_hour(user_id, msg_hour)
    except Exception as err:
        update.message.reply_text("DB error") # check this
        return
    db_change_event.set()
    logger.info(f"{user_id} updated 'send_msg_hour' as {msg_hour}.")
    update.message.reply_text(f"Messaging hour set successfully!")  # search DB to inform user if he is subbed or not)


def unsub_command(update, context):
    """Allows to cancel subscription for weather messages."""
    user_id = update.message.from_user.id
    database.unsubscribe(user_id)
    db_change_event.set()
    logger.info(f"User: {user_id} unsubbed.")
    update.message.reply_text(f"Successfully unsubbed.")


def save_post_code_command(update, context):
    user_id = update.message.from_user.id
    post_code = ''.join(context.args)
    database.save_post_code(user_id, post_code)
    db_change_event.set()
    logger.info(f"Post code for user: {user_id} has been saved successfully.")
    update.message.reply_text(f"{post_code} saved successfully.")


def help_command(update, context):  # needs an update
    """Command displaying detailed informations about usage to the user."""

    msg = ("""I can show you the weather for any city in the world u ask!
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
    """)
    update.message.reply_text(msg)
