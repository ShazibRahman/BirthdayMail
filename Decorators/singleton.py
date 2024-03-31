import logging


def singleton_with_parameters(cls):
    instances = {}

    def inner(*args, **kwargs):
        key = (cls, args, tuple(kwargs.items()))
        if key not in instances:
            logging.info("initializing %s  with %s", cls.__name__, key)
            instances[key] = cls(*args, **kwargs)
        else:
            logging.info("reusing %s", key)
        return instances[key]

    return inner
