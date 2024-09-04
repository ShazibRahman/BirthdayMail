import logging
from functools import wraps


# a perfect example of an advantage of using closure in Python
def singleton_with_parameters(cls):
    instances = {}

    @wraps(cls)
    def inner(*args, **kwargs):
        key = (cls, args, tuple(kwargs.items()))
        if key not in instances:
            if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
                logging.debug("initializing %s  with %s", cls.__name__, key)
            instances[key] = cls(*args, **kwargs)
        else:
            logging.debug("reusing %s", key)
        return instances[key]

    return inner


def singleton(cls):
    instances = {}

    @wraps(cls)
    def inner(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return inner
