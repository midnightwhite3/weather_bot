import psycopg2 as psc
from settings import DB_NAME, DB_USER, DB_PSWRD, logger
import traceback
import re

# TODO: functions there are not yet completed. Error handling, conditional statements, any other actions
# to improve these functions
# TODO: write specified exceptions for funcs

sub_type = {
    'unsubbed': 0,
    'now': 1,
    'today': 2,
    'tomorrow': 3,
}


def is_time(time):
    try:
        return re.search(r"^(2[0-3]|[01]?[0-9]):([0-5]?[0-9]):([0-5]?[0-9])$", time).group()
    except AttributeError:
        return False


class DBConnection:
    """https://stackoverflow.com/questions/65053690/how-to-create-a-function-that-connects-executes-and-disconnects
    Context manager class. Logs in to DB. 'WITH' statement handles every DB operation. Commits changes and closes DB."""    # more in the link
    def __init__(self):
        """Initializes the connection and PSYCOPG2 cursor to handle DB actions."""
        self.connection = psc.connect(database=DB_NAME, user=DB_USER, password=DB_PSWRD)
        self.cur = self.connection.cursor()
    
    def __enter__(self):
        """Everything in 'WITH'."""
        return self.cur

    def __exit__(self, err_type, err_value, traceback):
        """Commits changes and closes the DB connection."""
        if err_type and err_value:
            self.connection.rollback()
        self.connection.commit()
        self.cur.close()
        self.connection.close()
        return False


def db_init(db_name, db_user, db_pswrd, db_host=None, db_port=None):
    """No needed anymore."""
    conn = psc.connect()
    cur = conn.cursor()
    return conn, cur;


def is_subbed(user_id: int):
    """Return if user is subbed or not. Not in use for now - SUBSCRIBE column dropped from DB,
    replaced by subbed_for"""
    with DBConnection() as cur:
        cur.execute(f"""SELECT * FROM "user" WHERE user_id = {user_id} AND subscribed""")
        return bool(cur.fetchone())


def user_exists(user_id: int):
    """Boolean return if user is present in DB or not."""
    try:
        with DBConnection() as cur:
            cur.execute(f"""SELECT user_id FROM "user" WHERE user_id = {user_id}""")
            return bool(cur.fetchone())
    except:
        logger.error(traceback.print_exc())
    # exists = bool(cur.fetchone())
    # if exists:
    #     return "User already exists."
    # return "User doesnt exist"


def store_user(user_id: int, user_name: str):
    """Saves user in the DB."""
    try:
        with DBConnection() as cur:
            cur.execute(f"""INSERT INTO "user" (user_id, user_name) VALUES
            ({user_id}, '{user_name}')""")
    except:
        logger.error(traceback.print_exc())


def is_location(user_id: int):
    """Boolean return if location for the user exists."""
    try:
        with DBConnection() as cur:
            cur.execute(f"""SELECT city FROM "user" WHERE user_id = {user_id}""")
            return bool(cur.fetchone())
    except:
        logger.error(traceback.print_exc())


def store_location(user_id: int, city: str):
    """Save location for the user in the DB."""
    try:
        with DBConnection() as cur:
            cur.execute(f"""UPDATE "user"
            SET city = '{city}'
            WHERE user_id = {user_id}""")
    except:
        logger.error(traceback.print_exc())


def subscribe(user_id: int, sub, msg_hour='06:00:00', city=None):
    """Saves subscription type for weather messages, hour on which user wants to get the message (default 6am),
    makes a timestamp."""
    try:
        with DBConnection() as cur:
            cur.execute(f"""UPDATE "user"
            SET subbed_for = {sub},
            city = '{city.title()}',
            subbed_date = current_timestamp,
            send_msg_hour = '{msg_hour}'
            WHERE user_id = {user_id}""")
    except:
        logger.error(traceback.print_exc())


def set_msg_hour(user_id: int, msg_hour):
    """Allows to change the weather message sending time."""
    try:
        with DBConnection() as cur:
            cur.execute(f"""UPDATE "user"
            SET send_msg_hour = '{msg_hour}'
            WHERE user_id = {user_id}""")
    except:
        logger.error(traceback.print_exc())


# def make_query():
#     cur.execute(
#         """SELECT city FROM "user";"""
#     )
#     return cur.fetchall()
