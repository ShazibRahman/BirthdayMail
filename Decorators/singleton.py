import logging


def singleton_with_parameters(cls):
    instances = {}

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

    def inner(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return inner
