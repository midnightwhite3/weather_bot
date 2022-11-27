from threading import Thread, Event
from time import time, strftime, localtime, sleep
from datetime import datetime
from handle_data import fetch_subs
import schedule
import signal
import csv
from settings import logger

# use threading timer instead of schedule? make timer dynamic to execute on midnight
# so every 24hr or when func started count time to midnight
now = datetime.now()

def write_subs():
    """Temporary to catch the return of scheduled Job. Looking for more
        sufficient method."""
    try:
        with open("subs.csv", 'w', newline="") as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow(['id', 'city', 'hour', 'subbed_for'])
            subs = fetch_subs()
            for sub in subs:
                csv_writer.writerow(sub)
        logger.info(f"Data saved to csv file. Regular task done.")
    except Exception as err:
        logger.error(f"Writing data error: {err}\n{type(err)}")


def read_subs() -> list:
    """Read subbed user from csv file."""
    subbed_users = []
    try:
        with open("subs.csv", "r") as f:
            csv_reader = csv.reader(f, delimiter=',')
            next(csv_reader)    # skip header
            for row in csv_reader:
                subbed_users.append(row)
            logger.info("Data read successfully.")
            return subbed_users
    except Exception as err:
        logger.error(f"Reading data error: {err}\n{type(err)}")


def get_subscribers():
    schedule.every().day.at("16:54:15").do(write_subs)
    while True:
        schedule.run_pending()

        sleep(1)


l = read_subs()
print([sorted(s) for s in l]) # sort subs by hour integer, this doesnt work, changes order
# if __name__ == "__main__":
#     subs = Thread(target=get_subscribers)
#     signal.signal(signal.SIGINT, signal.SIG_DFL) # allows ctrl + c exit
#     subs.start()
