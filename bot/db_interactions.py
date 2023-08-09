# db_interactions

from settings import SUBS_PATH
from . import db_change_event, logger, update_subs, tasks

def db_check():
    """Func waits for a call from DB using commands. If DB operations, related to subscriptions are made, call an event."""
    while True:
        db_change_event.wait()
        logger.info('Database data has changed. Starting protocol...')
        tasks.write_subs(SUBS_PATH)
        db_change_event.clear()
        logger.info('Exiting protocol.')
        update_subs.set()