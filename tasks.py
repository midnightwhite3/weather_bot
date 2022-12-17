from time import sleep
from datetime import datetime
import schedule
import csv
from settings import logger
from operator import itemgetter
from validators import is_hour_greater
import get_weather as gw
import os

"""According to python-telegram-bot docs threading may couse problems and it is better to use asyncio
library."""

# subprocess - lib
# schedule in a for loop using Queue? for sub msg hour func

# use threading timer instead of schedule? make timer dynamic to execute on midnight
# so every 24hr or when func started count time to midnight
# TODO: write an event class, for db changes, subs.csv changes, and any changes overall.
# TODO: instead of scheduler, create an event NEW_DAY, its gonna trigger daily routine
# like write subs -> create_sub_list -> 
# TODO: write task to delete old log files
# TODO: allow to save postal code along with city name, get post code from database, less problematic and faster?


def current_hr_m() -> str:
    return datetime.now().strftime("%H:%M")


def new_day():
    pass


def delete_logs(log_files: int):
    """Keeps last (log_files) log files, removes the rest."""
    logs = os.listdir(f"{os.getcwd()}\logs")
    # if len(logs) > log_files:
    print(logs) # always keep log_files number of files, back to it


def write_subs():   # add path as arg
    from handle_data import fetch_subs
    """Temporary to catch the return of scheduled Job. Looking for more
        sufficient method."""
    try:
        with open("subs.csv", 'w', newline="") as f:
            logger.info(f"Opening file: {f.name}")
            csv_writer = csv.writer(f)
            csv_writer.writerow(['id', 'city', 'hour', 'subbed_for'])
            subs = fetch_subs()
            for sub in subs:
                csv_writer.writerow(sub)
        logger.info(f"Data saved to {f.name} successfully. Closing.")
    except Exception as err:
        logger.error(f"Writing data error: {err}\n{type(err)}")


def read_subs() -> list:    # add path as arg
    """Read subbed user from csv file."""
    subbed_users = []
    try:
        with open("subs.csv", "r") as f:
            logger.info(f"Opening file: {f.name}")
            csv_reader = csv.reader(f, delimiter=',')
            next(csv_reader)    # skip header
            for row in csv_reader:
                subbed_users.append(row)
            logger.info(f"Data from {f.name} read successfully. Closing.")
            return subbed_users
    except Exception as err:
        logger.error(f"Reading data error: {err}\n{type(err)}")


def get_subscribers():  # add hour as arg
    """Scheduled job. Fetches subs from DB and saves them in a CSV file, at given time everyday."""
    schedule.every().day.at("00:01:00").do(write_subs)
    while True:
        schedule.run_pending()
        sleep(1)


def sort_sub_list() -> list:
    """Reads subs from CSV, sorts them by message_hour. Removes sub from list - now <= message_hour."""
    subs = sorted(read_subs(), key=itemgetter(2))
    subs = is_hour_greater(subs)
    return subs


def send_weather_msg(user_id, city, subbed_for, f1, f2, f3, bot) -> callable:
    """Send msg to the user."""
    func = [f1, f2, f3][subbed_for-1]   # list of weather_msg funcs, indexing by the subscription type
    post_code = gw.find_postal_code(city)
    bot.send_message(user_id, func(city, post_code))    # bot object. Sending message
    logger.info(f"Weather msg to user {user_id} has been sent.")


def check_sub_hour(update_subs, bot):
    """Creates a list of subscribers (tuples). Checks if the hour matches the sub_hour (yet to be improved, not efficient enough?),
    sends weather_msg. Goes idle if no subscribers left for the day."""
    subs = sort_sub_list() # new day event <- here
    while True:
        try:
            if update_subs.is_set():
                logger.info('New sub, updating list...')
                subs = sort_sub_list()
                update_subs.clear()
                logger.info('Subs message schedule list updated.')
            if subs[0][2][:5] == current_hr_m():    # 0-first user, 2-hour L element, :5-HH:MM format
                user_id = subs[0][0]
                city = subs[0][1]
                subbed_for = int(subs[0][3])
                send_weather_msg(user_id, city, subbed_for, gw.weather_now, gw.weather_today, gw.weather_tomorrow, bot)
                del subs[0]
            else:
                sleep(3) # potential problem - if subs number on given minute > 60s/sleep - the overall
                    # sleep time will exceed 1min. Look for solution. #up1 - write function for this part and use threading? #up2 - use QUEUE
        except IndexError:
            logger.info('No subs left for today. Going to sleep.')
            update_subs.wait()
