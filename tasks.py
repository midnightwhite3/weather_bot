from threading import Thread, Event
from time import time, strftime, localtime, sleep
from datetime import datetime
from handle_data import check_msg_hour
import schedule
import signal
import sys

# use threading timer instead of schedule? make timer dynamic to execute on midnight
# so every 24hr or when func started count time to midnight

now = datetime.now().time()
day_end = now.replace(hour=9, minute=42, second=0, microsecond=0)
day_end2 = now.replace(hour=9, minute=42, second=20, microsecond=0)

subscribers = []


def get_subscribers():
    global subscribers
    schedule.every().day.at("13:09:20").do(check_msg_hour)
    while True:
        schedule.run_pending()
        sleep(1)


if __name__ == "__main__":
    subs = Thread(target=get_subscribers)
    signal.signal(signal.SIGINT, signal.SIG_DFL) # allows ctrl + c exit
    subs.start()
