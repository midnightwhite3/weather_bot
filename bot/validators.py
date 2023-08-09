# bot -> validators.py

from errors import NoCity
from settings import MSGS

# def weather_msg_conditional(update, context, weather_func, weather_type: str, day=None):
#     """Function validates user input and returns the message.
#     update - object, contains info and data from telegram,
#     context - object, contains info and data about the status of the library (python telegram bot),
#     weather_func - one of the weather functions from internal weather module,
#     weather_type - string, used to fill the link to openweather, tells to look
#                 for forecats or today weather,
#     day - used if weather_type = 'forecast', openweather response for forecast
#         throws back data for few days forward, makes sure we get weather for the day we want.
#     """
#     user_id = update.message.from_user.id
#     user_msg = context.args
#     if len(user_msg) == 0:
#         return update.message.reply_text("You need to enter city name.")
#     elif len(user_msg) > 1:
#         if not my_utils.has_number(user_msg[-1]):
#             city = " ".join(user_msg)
#             post_code = weather.find_postal_code(city, user_id=user_id)
#         else:
#             city = " ".join(user_msg[:-1])
#             post_code = user_msg[-1]
#     else:
#         city = user_msg[0]
#         post_code = weather.find_postal_code(city, user_id=user_id)
#     if len(post_code) > 20:
#         update.message.reply_text(post_code)    # error_msg
#         logger.info(f"Post code couldn't be found for {city.upper()}.")
#     else:
#         update.message.reply_text({weather_func(city, post_code, weather_type, day=day, user_id=user_id)}) # <-- city and post code, maybe add it to gw.weather_message
#         logger.info(f"user_id: {update.message.from_user.id} | msg: {city} {post_code}")


def is_city_input(user_msg, update, reply_msg=MSGS['No city']):
    if len(user_msg) == 0:
        update.message.reply_text(reply_msg)
        raise NoCity()
    pass
