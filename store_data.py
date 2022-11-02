import psycopg2 as psc
from settings import DB_NAME, DB_USER, DB_PSWRD
# TODO: look at db_init. Dont want to conn and cur to just sit there always in script. Ask for
# if __name__ == main then call db_init, discord.
# TODO: define is_subbed
# TODO: functions there are not yet completed. Error handling, conditional statements, any other actions
# to improve these functions
# TODO: write a class for data handling?


def db_init(db_name, db_user, db_pswrd, db_host=None, db_port=None):
    conn = psc.connect()
    cur = conn.cursor()
    return conn, cur;


conn = psc.connect(database=DB_NAME, user=DB_USER, password=DB_PSWRD)
cur = conn.cursor()


def is_subbed():
    pass


def store_user(user_id: int, user_name: str):
    cur.execute(f"""INSERT INTO 'user' (user_id, user_name) VALUES
    ({user_id}, {user_name})""")
    conn.commit()
    conn.close()


def store_location(city: str, user_id: int):
    try:
        cur.execute(f"""UPDATE 'user'
        SET city = {city}
        WHERE user_id = {user_id}""")
    except:
        print('err')


def subscribe(user_id: int):
    cur.execute(f"""UPDATE 'user'
    SET subscribed = TRUE
    WHERE user_id = {user_id}""")
