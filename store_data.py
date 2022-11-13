import psycopg2 as psc
from settings import DB_NAME, DB_USER, DB_PSWRD, logger
import traceback
import re

# TODO: functions there are not yet completed. Error handling, conditional statements, any other actions
# to improve these functions
# TODO: write specified exceptions for funcs
# TODO: write try on db init to check if its connected if noit raise the error
# TODO: improve DBError traceback

sub_type = {
    'unsubbed': 0,
    'now': 1,
    'today': 2,
    'tomorrow': 3,
}                   # maybe unnecessary complication? just store it as it is (a word).

db_err = "I have data related problem, fixing this ASAP."


class DBError(Exception):
    def __init__(self, message="I have data related problem, fixing this ASAP.", *args):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


def is_time(time):
    try:
        return re.search(r"\b(2[0-3]|[01]?[0-9]):([0-5][0-9]):([0-5][0-9])\b", time).group()
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
        # try:
        return self.cur
        # except Exception as error:
        #     logger.error(f"ERROR: {error} | TYPE: {type(error)}")
        #     raise DBError()

    def __exit__(self, err_type, err_value, traceback):
        """Commits changes and closes the DB connection."""
        if err_type and err_value:
            self.connection.rollback()  # read about rollback
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
    try:
        with DBConnection() as cur:
            cur.execute(f"""SELECT * FROM "user" WHERE user_id = {user_id} AND subscribed""")
            return bool(cur.fetchone())
    except Exception as error:      # bad habit, better to write more specific exceptions - change it
        logger.error(f"ERROR: {error} | TYPE: {type(error)}")
        raise DBError() # needed for message feedback display at weather_bot.py


def user_exists(user_id: int):
    """Boolean return if user is present in DB or not."""
    try:
        with DBConnection() as cur:
            cur.execute(f"""SELECT user_id FROM "user" WHERE user_id = {user_id}""")
            return bool(cur.fetchone())
    except Exception as error:
        logger.error(f"ERROR: {error} | TYPE: {type(error)}")
        raise DBError()


def store_user(user_id: int, user_name: str):
    """Saves user in the DB."""
    try:
        with DBConnection() as cur:
            cur.execute(f"""INSERT INTO "user" (user_id, user_name) VALUES
            ({user_id}, '{user_name}')""")
    except:
        logger.error(traceback.print_exc())
        raise DBError()


def is_location(user_id: int):
    """Boolean return if location for the user exists."""
    try:
        with DBConnection() as cur:
            cur.execute(f"""SELECT city FROM "user" WHERE user_id = {user_id}""")
            return bool(cur.fetchone())
    except Exception as error:
        logger.error(f"ERROR: {error} | TYPE: {type(error)}")
        raise DBError()


def store_location(user_id: int, city: str):
    """Save location for the user in the DB."""
    try:
        with DBConnection() as cur:
            cur.execute(f"""UPDATE "user"
            SET city = '{city}'
            WHERE user_id = {user_id}""")
    except Exception as error:
        logger.error(f"ERROR: {error} | TYPE: {type(error)}")
        raise DBError()


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
    except Exception as error:
        logger.error(f"ERROR: {error} | TYPE: {type(error)}")
        raise DBError()


def unsubscribe(user_id: int):
    """Sets subscription to 0 in DB, which is unsubbed according to dictionary at the beggining of the file."""
    try:
        with DBConnection as cur:
            cur.execute(f"""Update "user"
            SET subbed_for = {sub_type['unsubbed']}
            WHERE user_id = {user_id}""")
    except Exception as error:
        logger.error(f"ERROR: {error} | TYPE: {type(error)}")
        raise DBError()


def set_msg_hour(user_id: int, msg_hour):
    """Allows to change the weather message sending time."""
    try:
        with DBConnection() as cur:
            cur.execute(f"""UPDATE "user"
            SET send_msg_hour = '{msg_hour}'
            WHERE user_id = {user_id}""")
    except Exception as error:
        logger.error(f"ERROR: {error} | TYPE: {type(error)}")
        raise DBError()


# def make_query():
#     cur.execute(
#         """SELECT city FROM "user";"""
#     )
#     return cur.fetchall()
