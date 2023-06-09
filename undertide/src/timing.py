from datetime import datetime
from functools import wraps
from src.logger import setup_logger

L = setup_logger()


def log_timing(func):
    """
    This is a decorator, which is useful when you want
    to add various behaviors to functions in a very reusable way.

    USAGE (sample function):

        @log_timing
        def print_hello():
            print('Hello')

    """

    @wraps(func)
    def wrapper():
        started_at = datetime.now()
        result = func()
        ended_at = datetime.now()
        delta = ended_at - started_at
        L.debug(f"Ran {func.__name__} in {delta}")
        return result

    return wrapper
