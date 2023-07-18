# query functions for databse operations
import errors
import settings

from api_calls import add_API_call
from connection import DBConnect


@DBConnect
def is_subbed(cur, user_id: int):
    """Return if user is subbed or not. Not in use for now - SUBSCRIBE column dropped from DB,
       replaced by subbed_for
    """
    cur.execute(f"""SELECT * FROM "user" WHERE user_id = {user_id} AND subscribed""")
    return bool(cur.fetchone())


@DBConnect
def fetch_subs(cur):
    """Fetches subbed users from DB."""
    query = """SELECT user_id, city, send_msg_hour, subbed_for, post_code, call_count
            FROM "user"
            WHERE subbed_for != 0"""
    cur.execute(query)
    return cur.fetchall()


@DBConnect
def user_exists(cur, user_id: int):
    """Boolean return if user is present in database."""
    query = """SELECT user_id FROM "user" WHERE user_id = %s"""
    data = (user_id,)
    cur.execute(query, data)
    return bool(cur.fetchone())


@DBConnect
def is_location(cur, user_id: int):
    """Boolean return if location for the user with given ID, exists."""
    query = """SELECT city FROM "user" WHERE user_id = %s"""
    data = (user_id,)
    cur.execute(query, data)
    if type(cur.fetchone()[0]) is not str: # fetchone returns a tuple
        return False
    return True


@DBConnect
def fetch_city(cur, user_id: int):
    query = """SELECT city from "user" WHERE user_id = %s"""
    data = (user_id,)
    cur.execute(query, data)
    city = cur.fetchone()[0]
    if type(city) is not str:
        raise errors.DBError(f"City not found for user: {user_id}.")
    return city


@DBConnect
def is_post_code(cur, user_id: int):
    """Checks if the post_code is in the database for the specific user."""
    query = """SELECT post_code FROM "user" WHERE user_id = %s"""
    data = (user_id,)
    cur.execute(query, data)
    if type(cur.fetchone()[0]) is not str: # fetchone returns a tuple
        return False
    return True


@DBConnect
def get_post_code(cur, user_id: int):
    """Fetches post_code from the databse."""
    query = """SELECT post_code from "user" WHERE user_id = %s"""
    data = (user_id,)
    cur.execute(query, data)
    post_code = cur.fetchone()[0]
    if type(post_code) is not str:
        raise errors.DBError(f"No post code in database for user: {user_id}.")
    return post_code


@DBConnect
def API_call_limitter(cur, user_id: int, call_limit=settings.CALL_LIMIT):
    query = """SELECT call_count FROM "user" WHERE user_id = %s"""
    data = (user_id,)
    cur.execute(query, data)
    call_count = cur.fetchone()[0]
    if call_count >= call_limit:
        raise errors.DBError(f"OPENWEATHER API calls for user: {user_id} has exceed it's limit for the day.")
    add_API_call(user_id)
