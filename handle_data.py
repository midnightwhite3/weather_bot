import psycopg2 as psc
from settings import DB_NAME, DB_USER, DB_PSWRD, logger
import traceback

# TODO: functions there are not yet completed. Error handling, conditional statements, any other actions
# to improve these functions
# TODO: write specified exceptions for funcs
# TODO: improve DBError traceback
# TODO: exception in DBError class to not duck type it in every function
# TODO: delete seconds from send_msg_hour? dont allow user to type seconds, just set them to 0?

# use check_msg_hour* subbed users, their time, sub type, city and id
# then async if sub command is called, call check_msg_hour* to get this new user,
# or just append it to the list of subbed (not only if sub command is called but
# when changes are made in db, such as - city, hour, sub type --> UPDATE INFO)
# CREATE A LIST EVERYDAY AT MIDNIGHT SORTED BY HOUR, SCHEDULE A TASK FOR THOSE HOURS
# WHEN A CHANGE IS MADE TO MSG HOUR COLUMN, UPDATE THE LIST

# F STRINGS WITH SQL -> BIG NONO

sub_type = {
    'unsubbed': 0,
    'now': 1,
    'today': 2,
    'tomorrow': 3,
}                   # maybe unnecessary complication? just store it as it is (a word).


class DBError(Exception):
    def __init__(self, message="I have data base related problem, fixing this ASAP.", *args):
        self.message = message
        super().__init__(self.message)


    def __str__(self):
        return self.message


# take a closer look to sql alchemy library, may be a better option.
# sql alchemy --> django, pure python to make advanced DB operations.
class DBConnection:
    """https://stackoverflow.com/questions/65053690/how-to-create-a-function-that-connects-executes-and-disconnects
    Context manager class. Logs in to DB. 'WITH' statement handles every DB operation. Commits changes and closes DB."""    # more in the link
    def __init__(self):
        """Initializes the connection and PSYCOPG2 cursor to handle DB actions."""
        try:
            self.connection = psc.connect(database=DB_NAME, user=DB_USER, password=DB_PSWRD)
            self.cur = self.connection.cursor()
            logger.info('Connected to database.')
        except psc.OperationalError as err:
            logger.error(f"Connection error occured, traceback: {err}\n{type(err)}")
            raise DBError()
    

    def __enter__(self):
        """Everything in 'WITH'."""
        return self.cur


    def __exit__(self, exc_type, exc_value, exc_tb):
        """Commits changes, closes the DB connection, manages exceptions."""
        if exc_type:
            logger.error(f"Following error occured:\n type: {exc_type}\nvalue: {exc_value}\ntraceback: {exc_tb}")
            self.connection.rollback()  # read about rollback
        self.connection.commit()
        logger.info("Changes commited.")
        self.cur.close()
        self.connection.close()
        logger.info('Database connection closed.')
        return False # returning True makes any exceptions silent, continues with code


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
            query = """SELECT user_id FROM "user" WHERE user_id = %s"""
            data = (user_id,)
            cur.execute(query, data)
            return bool(cur.fetchone())
    except Exception as error:
        logger.error(f"ERROR: {error} | TYPE: {type(error)}")
        raise DBError()


def store_user(user_id: int, user_name: str):
    """Saves user in the DB."""
    try:
        with DBConnection() as cur:
            cur.execute("""INSERT INTO "user"
            (user_id, user_name) 
            VALUES (%s, %s)""", (user_id, user_name))
    except:
        logger.error(traceback.print_exc())
        raise DBError()


def is_location(user_id: int):
    """Boolean return if location for the user exists."""
    try:
        with DBConnection() as cur:
            query = """SELECT city FROM "user" WHERE user_id = %s"""
            data = (user_id,)
            cur.execute(query, data)
            if type(cur.fetchone()[0]) is not str: # fetchone returns a tuple
                return False
            return True
    except Exception as error:
        logger.error(f"ERROR: {error} | TYPE: {type(error)}")
        raise DBError()


def store_location(user_id: int, city: str):
    """Save location for the user in the DB."""
    try:
        with DBConnection() as cur:
            update = """UPDATE "user"
                     SET city = %s
                     WHERE user_id = %s"""
            data = (city, user_id)
            cur.execute(update, data)
    except Exception as error:
        logger.error(f"ERROR: {error} | TYPE: {type(error)}")
        raise DBError()


def subscribe(user_id: int, sub, msg_hour='06:00:00', city=None):   # check why city set to none
    """Saves subscription type for weather messages, hour on which user wants to get the message (default 6am),
    makes a timestamp."""
    try:
        with DBConnection() as cur:
            update = """UPDATE "user"
                     SET subbed_for = %s,
                     city = %s,
                     subbed_date = current_timestamp,
                     send_msg_hour = %s
                     WHERE user_id = %s""" # can swap current_timestamp to datetime.now()
            data = (sub, city, msg_hour, user_id)
            cur.execute(update, data)
    except Exception as error:
        logger.error(f"ERROR: {error} | TYPE: {type(error)}")
        raise DBError()


def unsubscribe(user_id: int):
    """Sets subscription to 0 in DB, which is unsubbed according to dictionary at the beggining of the file."""
    try:
        with DBConnection() as cur:
            update = """UPDATE "user"
                     SET subbed_for = %s,
                     city = %s,
                     subbed_date = %s,
                     send_msg_hour = %s
                     WHERE user_id = %s"""
            data = (sub_type['unsubbed'], None, None, None, user_id)
            cur.execute(update, data)
    except Exception as error:
        logger.error(f"ERROR: {error} | TYPE: {type(error)}")
        raise DBError()


def set_msg_hour(user_id: int, msg_hour):
    """Allows to change the weather message sending time."""
    try:
        with DBConnection() as cur:
            update = """UPDATE "user"
                     SET send_msg_hour = %s
                     WHERE user_id = %s"""
            data = (msg_hour, user_id)
            cur.execute(update, data)
    except Exception as error:
        logger.error(f"ERROR: {error} | TYPE: {type(error)}")
        raise DBError()


def fetch_subs():
    try:
        with DBConnection() as cur:
            query = """SELECT user_id, city, send_msg_hour, subbed_for
                    FROM "user"
                    WHERE subbed_for != 0"""
            cur.execute(query)
            return  cur.fetchall()
    except Exception as error:
        logger.error(f"ERROR: {error} | TYPE: {type(error)}")
        raise DBError()
