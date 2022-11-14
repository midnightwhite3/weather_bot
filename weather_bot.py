from telegram.ext import *  # not a good habit to import all. Func names can overrirde themselves
import get_weather as gw
from settings import logger, telegram_key
import handle_data as hd
import traceback
import re

# TODO: enable daily message about the weather based on saved city?
# TODO: write dict for error messages and fetch them from there?
# TODO: validate all users input. One found - remove any special chars from city when calling weather functions
# TODO: create validators.py for user input validation
# TODO: check if msg hours includes timezoning, maybe user must specify it?
# TODO: no error message for user if daa isnt saved to DB

logger.info("Bot is running..")


def validate_sub_type(sub):
    try:
        return re.search(r"today|now|tomorrow", sub).group()
    except AttributeError:  # throws attr error when no match found
        return False


def weather_msg_conditional(update, context, weather_func):
    """Function validates user input and returns the message."""
    if len(context.args) == 0:
        return update.message.reply_text("You need to give the city name.") # return to stop func right there, if not it continues and returns 2 error messages
    elif len(context.args) > 1:       # check i user msg has more than 1 word
        if not gw.has_number(context.args[-1]):    # verify that the last word is a post code or not
            city = " ".join(context.args)       # if its not post code, that means all words are a city name
            post_code = gw.find_postal_code(city)  # in that case we look for the post code
        else:
            city = " ".join(context.args[:-1])      # in that case user gave us the post code himself
            post_code = context.args[-1]            # so we dont look it up
    else:                                           # if user msg has 1 word it means he gave just the city name
        city = context.args[0]
        post_code = gw.find_postal_code(city)      # so we look up the post code
    if len(post_code) > 20:     # if func doesnt find post_code it returns error_msg which is long
        update.message.reply_text(post_code)    # error_msg
        logger.info(f"Post code couldn't be found for {city.upper()}.")    # log for every lack of postcode
    else:                       # found post code, success
        update.message.reply_text(f"{city.title()} {post_code} | {weather_func(city, post_code)}")
        logger.info(f"user_id: {update.message.from_user.id} | msg: {city} {post_code}")      # log every time user eneters a msg with success


def today_weather_command(update, context):
    """Today weather."""
    weather_msg_conditional(update, context, gw.weather_today)


def tomorrow_weather_command(update, context):
    """Tomorrow weather."""
    weather_msg_conditional(update, context, gw.weather_tomorrow)


def now_weather_command(update, context):
    """Now weather."""
    weather_msg_conditional(update, context, gw.weather_now)


def save_city_command(update, context):
    """After simple validation stores city for user_id. If user does not exist, storing user first then city."""
    try:
        city = ' '.join(context.args)
        if gw.has_number(city):
            update.message.reply_text(f"{city.title()} is not a valid city name.")
        user_name = update.message.from_user.name
        user_id = update.message.from_user.id
        if not hd.user_exists(user_id):
            hd.store_user(user_id, user_name)
        hd.store_location(user_id, city)
        update.message.reply_text(f"{city.title()} has been saved successfully!")
        logger.info(f"{city.title()} for user {user_id} has been updated.")
    except:
        update.message.reply_text(traceback.print_exc())
        logger.error(traceback.print_exc())


def help_command(update, context):
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


def subscribe_command(update, context):
    user_id = update.message.from_user.id
    subbed = validate_sub_type(' '.join(context.args))      # if user didnt type sub type, returns False
    hour = hd.is_time(' '.join(context.args))
    msg = ""
    if type(subbed) == bool:
        update.message.reply_text(f"""You must specify subscription type.\nOptions are - tomorrow, today, now.\nExample:
        /sub new york today 08:00:00""")
        return
    sub = hd.sub_type[validate_sub_type(' '.join(context.args))]    # user typed sub type, use dict to convert it to numeric
    if type(hour) == bool:
        hour = '06:00:00'
        msg += (f"""You didn't specify hour or gave wrong format so I set it to be 06:00:00.\nTo change that, use '/set_hour HH:MM:SS'.""")
    if type((hour and subbed)) == str:
        city = " ".join(context.args[:-2])
    else:
        city = " ".join(context.args[:-1])
    hd.subscribe(user_id, sub, hour, city)
    update.message.reply_text(msg + f"Subbed successfully. You will receive weather for {city.title()} at {hour} everyday.")
    logger.info(f"SUB - user: {user_id} | subbed for: {sub}")


def set_msg_hour_command(update, context):
    user_id = update.message.from_user.id
    msg_hour = hd.is_time(' '.join(context.args))
    if not msg_hour:
        update.message.reply_text(f"""{msg_hour} is not valid. Make sure you use 24hr format. Example:\n06:00:00""")
        return
    try:
        hd.set_msg_hour(user_id, msg_hour)
    except Exception:
        update.message.reply_text("DB error")
        return
    logger.info(f"{user_id} updated 'send_msg_hour' as {msg_hour}.")
    update.message.reply_text(f"Messaging hour set successfully!")  # search DB to inform user if he is subbed or not)


def unsub_command(update, context):
    user_id = update.message.from_user.id
    pass


def error(update, context):
    """Func logs the error and returns EXPECTED errors msgs. If the error is not
        catched by the previous functions, it returns defined below message to the user."""
    logger.error(f"USER ID: {update.message.from_user.id} | MESSAGE: {update.message.text} | ERR: {context.error}")
    update.message.reply_text(f"Unexpected error occured. Try again later.")


if __name__ == '__main__':
    updater = Updater(telegram_key, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('today', today_weather_command))
    dp.add_handler(CommandHandler('now', now_weather_command))
    dp.add_handler(CommandHandler('tomorrow', tomorrow_weather_command))
    dp.add_handler(CommandHandler('help', help_command))
    dp.add_handler(CommandHandler('save_city', save_city_command))
    dp.add_handler(CommandHandler('sub', subscribe_command))
    dp.add_handler(CommandHandler('set_hour', set_msg_hour_command))
    dp.add_error_handler(error)

    updater.start_polling(2.0)
    updater.idle()
    