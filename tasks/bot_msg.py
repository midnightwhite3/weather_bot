# bot_msg.py

from telegram.error import BadRequest

import settings
import database
import weather
import my_utils
from tasks import write_subs

def send_weather_msg(user_id: int, city: str, subbed_for: int, bot) -> callable:
    """Send msg to the user."""
    D = {# move this to settings
        'now': None,
        'today': my_utils.today_date,
        'tomorrow': my_utils.tomorrow_str,
    }
    sub_day = [*D][subbed_for-1]   # list of weather_msg funcs, indexing by the subscription type
    post_code = weather.find_postal_code(city, user_id)
    weather_type = 'weather' if sub_day == 'now' else 'forecast'
    weather_func = weather.weather_now if sub_day == 'now' else weather.weather
    day = D[sub_day]
    msg_day = day() if day is not None else 'Now'
    msg = f"Daily weather for {city.title()} | {msg_day}\n\n"
    try:
        bot.send_message(user_id, msg + weather_func(city, post_code, weather_type, day=day))    # bot object. Sending message
        settings.logger.info(f"Weather msg to user {user_id} has been sent.")
    except BadRequest:
        database.delete_user(user_id)
        settings.logger.info(f"Task failed. User doesn't exist. Deleting user {user_id} from the database.")
        write_subs(settings.SUBS_PATH) # update after user deletion
        raise database.DBError("User doesn't exist and has been deleted.")
