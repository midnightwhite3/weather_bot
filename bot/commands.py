# commands.py

import my_utils
from settings import SUB_TYPE, logger
import database


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


def db_check():
    """Func waits for a call from DB using commands. If DB operations, related to subscriptions are made, call an event."""
    while True:
        db_change_event.wait()
        logger.info('Database data has changed. Starting protocol...')
        tasks.write_subs(SUBS_PATH)
        db_change_event.clear()
        logger.info('Exiting protocol.')
        update_subs.set()