# database connect.py
import psycopg2 as psc
from functools import wraps

import settings
import errors

### DB CONTEXT MANAGER ###
class DBConnection:
    """Context manager class. Logs in to DB. 'WITH' statement handles every DB operation. Commits changes and closes DB."""
    def __init__(self):
        """Initializes the connection and PSYCOPG2 cursor to handle DB actions."""
        try:
            self.connection = psc.connect(database=settings.DB_NAME, user=settings.DB_USER, password=settings.DB_PSWRD)
            self.cur = self.connection.cursor()
            settings.logger.info('Connected to database.')
        except psc.OperationalError as err:
            settings.logger.error(f"Connection error occured, traceback: {err}\n{type(err)}")
            raise errors.DBError()
    
    def __enter__(self):
        """Everything in 'WITH'."""
        return self.cur

    def __exit__(self, exc_type, exc_value, exc_tb):
        """Commits changes, closes the DB connection, manages exceptions."""
        if exc_type:
            settings.logger.error(f"Following error occured:\n type: {exc_type}\nvalue: {exc_value}\ntraceback: {exc_tb}")
            self.connection.rollback()  # read about rollback
        self.connection.commit()
        settings.logger.info("Changes commited.")
        self.cur.close()
        self.connection.close()
        settings.logger.info('Database connection closed.')
        return False # returning True makes any exceptions silent, continues with code


### DB CONNECT DECORATOR ###
def DBConnect(fn):
    """Database connection decorator for DBConnection context manager class.
       Target function takes cur as additional parameter.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            with DBConnection() as cur:
                return fn(cur, *args, **kwargs)
        except Exception as error:
            settings.logger.error(f"ERROR: {error} | TYPE {type(error)}")
            raise errors.DBError()
    return wrapper
