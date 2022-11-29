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
current_time = datetime.now()
now = f"{current_time.hour}:{current_time.minute}" # returns 22:8 instead of 22:08


def current_hr_m():
    current_time = datetime.now()
    now = f"{current_time.hour}:{current_time.minute}"
    return now


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


def create_sub_list():
    pass


def check_sub_hour():
    subs = sorted(read_subs(), key=itemgetter(2))   # sorts list by hour variable, write func for this, possible collisions in the future
    print(subs)
    subs = is_hour_greater(subs)
    print(subs)
    while len(subs) > 0:
        print(subs[0][2][:5], current_hr_m())
        if subs[0][2][:5] == current_hr_m():
            print('y')
            del subs[0]
        else:
            pass
        sleep(3)
    print('Done')

subs = sorted(read_subs(), key=itemgetter(2))
print(is_hour_greater(subs))


# musi sprawdzac czy dana godzina jest wczesniej niz aktualna, jesli tak, usunac element z listy
# write_subs()
# subs = sorted(read_subs(), key=itemgetter(2))
# hour = subs[0][2][:5]
# print(hour)

# write_subs()
# check_sub_hour()

# if __name__ == "__main__":
#     subs = Thread(target=get_subscribers)
#     signal.signal(signal.SIGINT, signal.SIG_DFL) # allows ctrl + c exit
#     subs.start()
