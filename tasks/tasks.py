# tasks.py

import schedule
from time import sleep
from threading import Event

import tasks
import database
import my_utils
from settings import logger, SUBS_PATH, KEEP_N_LOGS, NEW_DAY, LOGS_PATH


"""According to python-telegram-bot docs threading may couse problems and it is better to use asyncio
library."""

# subprocess - lib
# schedule in a for loop using Queue? for sub msg hour func

# use threading timer instead of schedule? make timer dynamic to execute on midnight
# so every 24hr or when func started count time to midnight
# TODO: write an event class, for db changes, subs.csv changes, and any changes overall.


def new_day_tasks():
    """Scheduled jobs. Done on NEW_DAY hour, specified in settings.py"""
    schedule.every().day.at(NEW_DAY).do(tasks.write_subs, subs_path=SUBS_PATH)
    schedule.every().day.at(NEW_DAY).do(tasks.delete_logs, logs_path=LOGS_PATH,  n_logs=KEEP_N_LOGS)
    schedule.every().day.at(NEW_DAY).do(database.remove_API_calls)
    while True:
        schedule.run_pending()
        sleep(10)


def check_sub_hour(update_subs: Event, bot):
    """ Creates a list of subscribers (tuples). Checks if the hour matches the sub_hour (yet to be improved, not efficient enough?),
    sends weather_msg. Goes idle if no subscribers left for the day.
    """
    subs = tasks.sort_sub_list() # new day event <- here???
    while True:
        try:
            if update_subs.is_set():
                logger.info('New sub, updating list...')
                subs = tasks.sort_sub_list()
                update_subs.clear()
                logger.info('Subs message schedule list updated.')
            if subs[0][2][:5] == my_utils.parsers.current_hr_m():    # 0-first user, 2-hour L element, :5-HH:MM format
                # user_id = subs[0][0]
                # city = subs[0][1]
                # subbed_for = int(subs[0][3])
                user_id, city, subbed_for, *_ = subs
                tasks.send_weather_msg(user_id, city, int(subbed_for), bot)
                del subs[0]
            else:
                sleep(3) # potential problem - if subs number on given minute > 60s/sleep - the overall
                    # sleep time will exceed 1min. Look for solution. #up1 - write function for this part and use threading? #up2 - use QUEUE
        except IndexError:
            logger.info('No subs left for today. Going to sleep.')
            update_subs.wait()
