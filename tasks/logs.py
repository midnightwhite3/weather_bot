# logs.py

import os

from settings import logger


def delete_logs(logs_path: str, n_logs: int=None):
    """'n_log' - the number of log files you want keep.
    Creates a list of log files sorted by creation date by default.
    Deletes files starting from the oldest.
    """
    logs = os.listdir(logs_path)
    if len(logs) > n_logs:
        f_to_remove = len(logs) - n_logs
        logger.info("Deleting old log files...")
        for _ in range(f_to_remove):
            filename = os.path.join(logs_path, logs[0])
            del logs[0]
            os.remove(filename)
        logger.info(f"Number of logs deleted: {f_to_remove}. Logs remaining: {len(logs)}")