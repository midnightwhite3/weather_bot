from threading import Thread
from time import time, strftime, localtime, sleep
from datetime import datetime
from handle_data import check_msg_hour

now = datetime.now().time()
day_end = now.replace(hour=0, minute=0, second=20, microsecond=0)

subscribers = []


def get_subscribers():
    global subscribers
    """add checking for changes in db msg hour column"""
    while True:
        if now > day_end:
            subscribers = check_msg_hour()
        sleep(15)
