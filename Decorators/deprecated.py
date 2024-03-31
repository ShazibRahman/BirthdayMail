import warnings
from functools import wraps
import logging


def deprecated(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logging.warning("Call to deprecated method {}.".format(func.__name__))
        return func(*args, **kwargs)

    return wrapper
