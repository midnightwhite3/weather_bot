# database update operations (may separate deletions and insertions to different
# files in the future)

import settings
from .connection import DBConnect

### INSERTIONS or functions which main idea is to save/update data. ###
@DBConnect
def save_user(cur, user_id: int, user_name: str):
    """Saves user ID and it's name in the database."""
    cur.execute("""INSERT INTO "user"
    (user_id, user_name) 
    VALUES (%s, %s)""", (user_id, user_name))
    settings.logger.info(f"User {user_id} is now in database.")


@DBConnect
def save_post_code(cur, user_id: int, post_code):
    """Saves post_code in the database for desired user."""
    if user_id == None: return
    update = """UPDATE "user"
             SET post_code = %s
             WHERE user_id = %s"""
    data = (post_code, user_id)
    cur.execute(update, data)
    settings.logger.info(f"Post code saved for user: {user_id}") # put a city name in there


@DBConnect
def save_location(cur, user_id: int, city: str):
    """Save location for the user with given ID in the DB."""
    update = """UPDATE "user"
             SET city = %s
             WHERE user_id = %s"""
    data = (city, user_id)
    cur.execute(update, data)
    settings.logger.info(f"User: {user_id} has just changed location to {city}.")


@DBConnect
def subscribe(cur, user_id: int, sub, msg_hour='06:00:00', city=None):
    """Saves:
       - subscription type for weather messages,
       - hour on which user wants to get the message (default 6am),
       - city if the user specified, NONE by default,
       - makes a timestamp.
    """
    update = """UPDATE "user"
             SET subbed_for = %s,
             city = %s,
             subbed_date = current_timestamp,
             send_msg_hour = %s
             WHERE user_id = %s""" # can swap current_timestamp to datetime.now()
    data = (sub, city, msg_hour, user_id)
    cur.execute(update, data)
    settings.logger.info(f"User: {user_id} has just subbed for {sub}.")


### DELETIONS or functions which main idea is to delete or update data to 0. ###
@DBConnect
def unsubscribe(cur, user_id: int):
    """Sets subscription to 0 in DB, which is unsubbed according to dictionary
       at the beggining of the file.
    """
    update = """UPDATE "user"
             SET subbed_for = %s,
             city = %s,
             subbed_date = %s,
             send_msg_hour = %s
             WHERE user_id = %s"""
    data = (settings.SUB_TYPE['unsubbed'], None, None, None, user_id)
    cur.execute(update, data)
    settings.logger.info(f"User: {user_id} just unsubbed.")


@DBConnect
def delete_user(cur, user_id: int):
    """Deletes user from DB."""
    update = """DELETE FROM "user"
             WHERE user_id = %s"""
    data = (user_id,)
    cur.execute(update, data)
    settings.logger.info(f"User: {user_id} has been deleted from database.")



@DBConnect
def remove_post_code(cur, user_id: int):
    """Sets desired user's post code to NONE. Post code deletion."""
    update = """UPDATE "user"
             SET post_code = %s
             WHERE user_id = %s"""
    data = (None, user_id)
    cur.execute(update, data)
    settings.logger.info(f"Post code for user {user_id} has been deleted.")


@DBConnect
def set_msg_hour(cur, user_id: int, msg_hour):
    """Allows to change the weather message sending time."""
    update = """UPDATE "user"
             SET send_msg_hour = %s
             WHERE user_id = %s"""
    data = (msg_hour, user_id)
    cur.execute(update, data)
