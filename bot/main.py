import traceback
import signal
from threading import Event, Thread

from telegram.ext import Updater, CommandHandler
from telegram.bot import Bot

import my_utils 
import weather
import tasks
import database
from settings import logger, TELEGRAM_KEY, SUBS_PATH, SUB_TYPE



# TODO: check if msg hours includes timezoning, maybe user must specify it? look pytz
# TODO: write func -> send message to subbed users when bot is going offline and when its up?

def weather_msg_conditional(update, context, weather_func, weather_type: str, day=None):
    """Function validates user input and returns the message.
    update - object, contains info and data from telegram,
    context - object, contains info and data about the status of the library (python telegram bot),
    weather_func - one of the weather functions from internal weather module,
    weather_type - string, used to fill the link to openweather, tells to look
                for forecats or today weather,
    day - used if weather_type = 'forecast', openweather response for forecast
        throws back data for few days forward, makes sure we get weather for the day we want.
    """
    user_id = update.message.from_user.id
    user_msg = context.args
    if len(user_msg) == 0:
        return update.message.reply_text("You need to enter city name.")
    elif len(user_msg) > 1:
        if not my_utils.has_number(user_msg[-1]):
            city = " ".join(user_msg)
            post_code = weather.find_postal_code(city, user_id=user_id)
        else:
            city = " ".join(user_msg[:-1])
            post_code = user_msg[-1]
    else:
        city = user_msg[0]
        post_code = weather.find_postal_code(city, user_id=user_id)
    if len(post_code) > 20:
        update.message.reply_text(post_code)    # error_msg
        logger.info(f"Post code couldn't be found for {city.upper()}.")
    else:
        update.message.reply_text({weather_func(city, post_code, weather_type, day=day, user_id=user_id)}) # <-- city and post code, maybe add it to gw.weather_message
        logger.info(f"user_id: {update.message.from_user.id} | msg: {city} {post_code}")


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

# TODO: divide it to more specific commands like
# ^^ /commands, /details, /help for example.
# TODO: update help messages.
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

# TODO: rewrite this to be more readable
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
    update.message.reply_text(f"Post code saved successfully.")


def error(update, context):
    """Func logs the error and returns EXPECTED errors msgs. If the error is not
        catched by the previous functions, it returns defined below message to the user."""
    logger.error(f"USER ID: {update.message.from_user.id} | MESSAGE: {update.message.text} | ERR: {context.error}")
    update.message.reply_text(f"Unexpected error occured. Try again later.")


def db_check(event):
    """Func waits for a call from DB using commands. If DB operations, related to subscriptions are made, call an event."""
    while True:
        event.wait()
        logger.info('Database data has changed. Starting protocol...')
        tasks.write_subs(SUBS_PATH)
        event.clear()
        logger.info('Exiting protocol.')
        update_subs.set()


if __name__ == '__main__':
    logger.info("Bot is running..")

    tasks.write_subs(SUBS_PATH)
    
    updater = Updater(TELEGRAM_KEY, use_context=True)
    bot = Bot(token=TELEGRAM_KEY)
    dp = updater.dispatcher
    db_change_event = Event()
    update_subs = Event()

    dp.add_handler(CommandHandler('today', today_weather_command))
    dp.add_handler(CommandHandler('now', now_weather_command))
    dp.add_handler(CommandHandler('tomorrow', tomorrow_weather_command))
    dp.add_handler(CommandHandler('help', help_command))
    dp.add_handler(CommandHandler('save_city', save_city_command))
    dp.add_handler(CommandHandler('sub', subscribe_command))
    dp.add_handler(CommandHandler('set_hour', set_msg_hour_command))
    dp.add_handler(CommandHandler('unsub', unsub_command))
    dp.add_handler(CommandHandler('save_pc', save_post_code_command))
    dp.add_error_handler(error)

    DB_subs_to_csv = Thread(target=tasks.new_day_tasks)
    sub_msg_send = Thread(target=tasks.check_sub_hour, args=(update_subs, bot))
    check = Thread(target=db_check, args=(db_change_event,))
    signal.signal(signal.SIGINT, signal.SIG_DFL) # allows ctrl + c exit
    DB_subs_to_csv.start()
    sub_msg_send.start()
    check.start()
    
    updater.start_polling(2.0)
    updater.idle()
    