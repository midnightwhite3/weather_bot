import psycopg2 as psc
from settings import DB_NAME, DB_USER, DB_PSWRD, logger
import traceback

# TODO: look at db_init. Dont want to conn and cur to just sit there always in script. Ask for
# if __name__ == main then call db_init, discord.
# TODO: functions there are not yet completed. Error handling, conditional statements, any other actions
# to improve these functions
# TODO: write a class for data handling?

sub_type = {
    0: 'unsubbed',
    1: 'today',
    2: 'tomorrow',
}


class DBConnection:
    """https://stackoverflow.com/questions/65053690/how-to-create-a-function-that-connects-executes-and-disconnects""" # learn about context manager more
    def __init__(self):
        self.connection = psc.connect(database=DB_NAME, user=DB_USER, password=DB_PSWRD)
        self.cur = self.connection.cursor()
    
    def __enter__(self):
        return self.cur

    def __exit__(self, err_type, err_value, traceback):
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
    with DBConnection() as cur:
            cur.execute(f"""SELECT user_id FROM "user" WHERE user_id = {user_id}""")
            return bool(cur.fetchone())
    # exists = bool(cur.fetchone())
    # if exists:
    #     return "User already exists."
    # return "User doesnt exist"


def store_user(user_id: int, user_name: str):
    with DBConnection() as cur:
        cur.execute(f"""INSERT INTO "user" (user_id, user_name) VALUES
        ({user_id}, '{user_name}')""")


def store_location(user_id: int, city: str):
    with DBConnection() as cur:
        try:
            cur.execute(f"""UPDATE "user"
            SET city = '{city}'
            WHERE user_id = {user_id}""")
        except:
            logger.ERROR(traceback.print_exc())


def subscribe(user_id: int, sub, msg_hour='06:00:00'):
    with DBConnection() as cur:
        cur.execute(f"""UPDATE "user"
        SET subbed_for = {sub},
        subbed_date = current_timestamp,
        send_msg_hour = '{msg_hour}'
        WHERE user_id = {user_id}""")


def set_msg_hour(user_id: int, msg_hour):
    with DBConnection() as cur:
        cur.execute(f"""UPDATE "user"
        SET send_msg_hour = '{msg_hour}'
        WHERE user_id = {user_id}""")


# def make_query():
#     cur.execute(
#         """SELECT city FROM "user";"""
#     )
#     return cur.fetchall()
