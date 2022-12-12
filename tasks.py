from time import sleep
from datetime import datetime
from handle_data import sub_type
import schedule
import csv
from settings import logger
from operator import itemgetter
from validators import is_hour_greater

# subprocess - lib
# schedule in a for loop using Queue? for sub msg hour func

# use threading timer instead of schedule? make timer dynamic to execute on midnight
# so every 24hr or when func started count time to midnight
# TODO: write an event class, for db changes, subs.csv changes, and any changes overall.
# TODO: instead of scheduler, create an event NEW_DAY, its gonna trigger daily routine
# like write subs -> create_sub_list -> 
# TODO: write task to delete old log files


def current_hr_m() -> str:
    return datetime.now().strftime("%H:%M")


def get_sub_type(sub, f1, f2, f3):
    func = [f1, f2, f3][sub-1]
    return func


def write_subs():
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


def read_subs() -> list:
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


def get_subscribers():  # function only for schedule purposes - bad? Just put write_subs in main?
    """Scheduled job. Fetches subs from DB and saves them in a CSV file, at given time everyday."""
    schedule.every().day.at("12:39:00").do(write_subs)
    while True:
        schedule.run_pending()
        sleep(1)


def sort_sub_list() -> list:
    """Reads subs from CSV, sorts them by message_hour. Removes sub from list - now <= message_hour."""
    subs = sorted(read_subs(), key=itemgetter(2))
    subs = is_hour_greater(subs)
    return subs


def send_weather_msg(user_id, update): # get the id of user and send the msg
    """Send msg to the user."""
    get_sub_type()
    update.message.reply_text(f"") # stopped here, get back to it
    print('msg sent.')


def check_sub_hour(update_subs):
    """Creates a list of subscribers (tuples). Checks if the hour matches the sub_hour (yet to be improved, not efficient enough?),
    sends weather_msg. Goes idle if no subscribers left for the day."""
    subs = sort_sub_list() # new day event needs to be created here.
    while True:
        try:
            if update_subs.is_set():
                logger.info('New sub, updating list...')
                subs = sort_sub_list()
                update_subs.clear()
                logger.info('Subs message schedule list updated.')
            if subs[0][2][:5] == current_hr_m():    # 0-first user, 2-hour L element, :5-HH:MM format
                user_id = subs[0][0]
                send_weather_msg(user_id)
                del subs[0]
            else:
                sleep(3) # potential problem - if subs number on given minute > 60s/sleep - the overall
                    # sleep time will exceed 1min. Look for solution. #up1 - write function for this part and use threading? #up2 - use QUEUE
        except IndexError:
            logger.info('No subs left for today. Going to sleep.')
            update_subs.wait()
