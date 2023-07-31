# general.py

import datetime
import time


def today_date() -> datetime.date:
    """Returns today's date as datetime object."""
    return datetime.datetime.today().date()


def tomorrow_str() -> str:
    """Returns tomorrow in yyyy/mm/dd format as str."""
    return time.strftime("%Y-%m-%d", time.gmtime(time() + 86400))


def mps_to_kmh(speed: float) -> float:
    """Takes the speed in m/s and converts it to km/h."""
    return speed * 3.6


def hour_now_str() -> str:
    """Returns current hour and minute as string."""
    return datetime.datetime.now().strftime("%H:%M")


def current_hr_m() -> str:
    return datetime.datetime.now().strftime("%H:%M") # these 2 are the same


def file_extension_strip(filename: str, ext: str) -> str:
    """Removes file extensions from filenames."""
    return filename.strip(ext)
