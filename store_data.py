import psycopg2 as psc
from settings import DB_NAME, DB_USER, DB_PSWRD
# TODO: look at db_init. Dont want to conn and cur to just sit there always in script. Ask for
# if __name__ == main then call db_init, discord.
# TODO: define is_subbed
# TODO: functions there are not yet completed. Error handling, conditional statements, any other actions
# to improve these functions
# TODO: write a class for data handling?
# TODO: add column to DB: for which weather does user want ot sub for.
# TODO: add column to DB: define an houir on which user wants to receive weather_message.
# TODO: subscribed column is unneccessary? due to sub type, 0/1/2 no sub/today/tomorrow


sub_type = {
    0: 'unsubbed',
    1: 'today',
    2: 'tomorrow',
}


def db_init(db_name, db_user, db_pswrd, db_host=None, db_port=None):
    conn = psc.connect()
    cur = conn.cursor()
    return conn, cur;


conn = psc.connect(database=DB_NAME, user=DB_USER, password=DB_PSWRD) # replace it with db_init func later or __name__ == main?
cur = conn.cursor()


def is_subbed(user_id: int):
    """Return if user is subbed or not. Not in use for now - SUBSCRIBE column dropped from DB,
    replaced by subbed_for"""
    cur.execute(f"""SELECT * FROM "user" WHERE user_id = {user_id} AND subscribed""")
    return bool(cur.fetchone())


def store_user(user_id: int, user_name: str):
    cur.execute(f"""INSERT INTO "user" (user_id, user_name) VALUES
    ({user_id}, '{user_name}')""")
    conn.commit()
    conn.close()


def store_location(city: str, user_id: int):
    # try:
        cur.execute(f"""UPDATE "user"
        SET city = '{city}'
        WHERE user_id = {user_id}""")
        conn.commit()
        conn.close()
    # except:
    #     print('err')


def subscribe(user_id: int, sub, msg_hour='06:00:00'):
    cur.execute(f"""UPDATE "user"
    SET subbed_for = {sub},
    subbed_date = current_timestamp,
    send_msg_hour = '{msg_hour}'
    WHERE user_id = {user_id}""")
    conn.commit()
    conn.close()
