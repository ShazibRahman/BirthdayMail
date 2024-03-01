import warnings

def deprecated(func):
    def wrapper(*args, **kwargs):
        warnings.warn("Call to deprecated method {}.".format(func.__name__), category=DeprecationWarning, stacklevel=2)
        return func(*args, **kwargs)
    return wrapper
