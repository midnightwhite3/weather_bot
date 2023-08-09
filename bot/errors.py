# bot -> errors.py

import settings


class NoCity(Exception):
    def __init__(self, message=settings.MSGS['No city'], *args):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message