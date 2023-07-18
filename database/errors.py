# database errors.py

class DBError(Exception):
    def __init__(self, message="I have data base related problem, fixing this ASAP.", *args):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message
