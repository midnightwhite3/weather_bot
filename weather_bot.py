from telegram.ext import *  # not a good habit to import all. Func names can overrirde themselves
import get_weather
from settings import logger, telegram_key
import store_data
import traceback
# from .data import subscriptions

# TODO: possibility to save your own location and make program fetch weather based on this location?
# TODO: enable daily message about the weather based on saved city?
# TODO: check if telegram allows users to save their location.
# TODO: fetch the location and allow the command funcs to when len(context.args) == 0
# no location was given, it means user wants the weather for his own.

logger.info("Bot is running..")


def weather_msg_conditional(update, context, weather_func):
    """Function validates user input and returns the message."""
    if len(context.args) == 0:
        return update.message.reply_text("You need to give the city name.") # return to stop func right there, if not it continues and returns 2 error messages
    elif len(context.args) > 1:       # check i user msg has more than 1 word
        if not get_weather.has_number(context.args[-1]):    # verify that the last word is a post code or not
            city = " ".join(context.args)       # if its not post code, that means all words are a city name
            post_code = get_weather.find_postal_code(city)  # in that case we look for the post code
        else:
            city = " ".join(context.args[:-1])      # in that case user gave us the post code himself
            post_code = context.args[-1]            # so we dont look it up
    else:                                           # if user msg has 1 word it means he gave just the city name
        city = context.args[0]
        post_code = get_weather.find_postal_code(city)      # so we look up the post code
    if len(post_code) > 20:     # if func doesnt find post_code it returns error_msg which is long
        update.message.reply_text(post_code)    # error_msg
        logger.info(f"Post code couldn't be found for {city.upper()}.")    # log for every lack of postcode
    else:                       # found post code, success
        update.message.reply_text(f"{city.title()} {post_code} | {weather_func(city, post_code)}")
        logger.info(f"user_id: {update.message.from_user.id} | msg: {city} {post_code}")      # log every time user eneters a msg with success


def today_weather_command(update, context):
    """Today weather."""
    weather_msg_conditional(update, context, get_weather.weather_today)


def tomorrow_weather_command(update, context):
    """Tomorrow weather."""
    weather_msg_conditional(update, context, get_weather.weather_tomorrow)


def now_weather_command(update, context):
    """Now weather."""
    weather_msg_conditional(update, context, get_weather.weather_now)


def save_city_command(update, context):
    try:
        city = ' '.join(context.args)
        user_name = update.message.from_user.name
        user_id = update.message.from_user.id
        if not store_data.user_exists(user_id):
            store_data.store_user(user_id, user_name)
        store_data.store_location(user_id, city)
        update.message.reply_text(f"{city.title()} has been saved successfully!")
        logger.info(f"{city.title()} for user {user_id} has been updated.")
    except:
        update.message.reply_text(traceback.print_exc())
        logger.error(traceback.print_exc())


def help_command(update, context):
    """Command displaying detailed informations about usage to the user."""
    msg = """I can show you the weather for any city in the world u ask!
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
    """
    update.message.reply_text(msg)


def subscribe_command(update, context):
    pass


# def handle_message(update, context):
#     text = str(update.message.text).lower()
#     update.message.reply_text(text)


def error(update, context):
    """Func logs the error and returns EXPECTED errors msgs. If the error is not
        catched by the previous functions, it returns defined below message to the user."""
    logger.error(f"Update {update} caused error {context.error}")
    update.message.reply_text(f"Unexpected error occured. Try again later.")


if __name__ == '__main__':
    updater = Updater(telegram_key, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('today', today_weather_command))
    dp.add_handler(CommandHandler('now', now_weather_command))
    dp.add_handler(CommandHandler('tomorrow', tomorrow_weather_command))
    # dp.add_handler(MessageHandler(Filters.text, handle_message))
    dp.add_handler(CommandHandler('help', help_command))
    dp.add_handler(CommandHandler('save_city', save_city_command))
    dp.add_error_handler(error)

    updater.start_polling(2.0)
    updater.idle()
    