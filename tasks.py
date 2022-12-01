from threading import Thread, Event
from time import time, strftime, localtime, sleep
from datetime import datetime
from handle_data import fetch_subs
import schedule
import signal
import csv
from settings import logger
from operator import itemgetter
from validators import is_hour_greater

# use threading timer instead of schedule? make timer dynamic to execute on midnight
# so every 24hr or when func started count time to midnight
# TODO: write an event class, for db changes, subs.csv changes, and any changes overall.
# TODO: instead of scheduler, create an event NEW_DAY, its gonna trigger daily routine
# like write subs -> create_sub_list -> 

now = datetime.now().strftime("%H:%M") # returns 22:8 instead of 22:08

def current_hr_m():
    return datetime.now().strftime("%H:%M")


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
    """Scheduled job. Fetches subs from DB and saves them in a CSV file, at given time everyday."""
    schedule.every().day.at("16:54:15").do(write_subs)
    while True:
        schedule.run_pending()
        sleep(1)


def create_sub_list():
    """Reads subs from CSV, sorts them by message_hour. Removes sub from list - now <= message_hour."""
    subs = sorted(read_subs(), key=itemgetter(2))   # sorts list by hour variable, write func for this, possible collisions in the future
    subs = is_hour_greater(subs)
    return subs


def check_sub_hour():
    subs = sorted(read_subs(), key=itemgetter(2))   # sorts list by hour variable, write func for this, possible collisions in the future
    subs = is_hour_greater(subs)
    while len(subs) > 0:
        if subs[0][2][:5] == current_hr_m():    # 0-first user, 2-hour L element, :5-HH:MM format
            print('y')
            del subs[0]
        else:
            pass
        sleep(3) # potential problem - if subs number on given minute > 60s/sleep - the overall
                 # sleep time will exceed 1min. Look for solution.
    print('Done')


if __name__ == "__main__":
    DB_subs_to_csv = Thread(target=get_subscribers)
    sub_msg_send = Thread(target=check_sub_hour)
    signal.signal(signal.SIGINT, signal.SIG_DFL) # allows ctrl + c exit
    DB_subs_to_csv.start()
    sub_msg_send.start()