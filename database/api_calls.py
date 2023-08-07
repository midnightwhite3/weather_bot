# OPENWEATHER API calls functions.
# This file may be redundant, maybe move funcs to updates.py .

import settings
from . import errors

from .connection import DBConnect

# add_api_call and call limitter can be doen with only SQL statements.
# change DBError message for this function as status error (wrong error message)
@DBConnect
def add_API_call(cur, user_id: int):
    update = """UPDATE "user"
                SET call_count = call_count + 1
                WHERE user_id = %s"""
    data = (user_id,)
    cur.execute(update, data)
    settings.logger.info(f"USER: {user_id}, just made a call to OPENWEATHER API.")


@DBConnect
def API_call_limitter(cur, user_id: int, call_limit=settings.CALL_LIMIT):
    query = """SELECT call_count FROM "user" WHERE user_id = %s"""
    data = (user_id,)
    cur.execute(query, data)
    call_count = cur.fetchone()[0]
    if call_count >= call_limit:
        raise errors.DBError(f"OPENWEATHER API calls for user: {user_id} has exceed it's limit for the day.")
    add_API_call(user_id)


@DBConnect
def remove_API_calls(cur):
    """Removes API calls for users where call number is bigger than zero."""
    update = """UPDATE "user"
             SET call_count = 0
             WHERE call_count > 0""" # just reset all without conditioning? Check performance
    cur.execute(update)
    settings.logger.info(f"New day task. Resetting API calls for all users.")
