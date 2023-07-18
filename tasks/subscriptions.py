# subscriptions.py

import operator
import csv

import database
import my_utils
from settings import logger, SUBS_PATH


def write_subs(subs_path: str):
    """ Temporary to catch the return of scheduled Job. Looking for more
    sufficient method.
    """
    try:
        with open(subs_path, 'w', newline="") as f:
            logger.info(f"Opening file: {f.name}")
            csv_writer = csv.writer(f)
            csv_writer.writerow(['id', 'city', 'hour', 'subbed_for', 'post_code', 'call_count'])
            subs = database.fetch_subs()
            for sub in subs:
                csv_writer.writerow(sub)
        logger.info(f"Data saved to {f.name} successfully. Closing.")
    except Exception as err: # change this
        logger.error(f"Writing data error: {err}\n{type(err)}")


def read_subs(subs_path: str) -> list:
    """Read subbed users from csv file."""
    subbed_users = []
    try:
        with open(subs_path, "r") as f:
            logger.info(f"Opening file: {f.name}")
            csv_reader = csv.reader(f, delimiter=',')
            next(csv_reader)    # skip header
            for row in csv_reader:
                subbed_users.append(row)
            logger.info(f"Data from {f.name} read successfully. Closing.")
            return subbed_users
    except Exception as err: # change this
        logger.error(f"Reading data error: {err}\n{type(err)}")


def sort_sub_list() -> list:
    """ Reads subs from CSV, sorts them by message_hour.
        Removes sub from list - now <= message_hour.
    """
    subs = sorted(read_subs(SUBS_PATH), key=operator.itemgetter(2))
    subs = my_utils.validators.is_hour_greater(subs)
    return subs
