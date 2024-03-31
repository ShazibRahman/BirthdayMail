import logging

from typing import Any, Callable
from functools import wraps


def sneaky_throws(func: Callable) -> Any:
    """
        A decorator that wraps a function and catches any exceptions that occur during its execution.

        Parameters:
        func (Callable): The function to be wrapped.

        Returns:
        Any: The return value of the wrapped function, or None if an exception is caught.
"""
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(e)

    return wrapper


if __name__ == '__main__':
    @sneaky_throws
    def foo():
        return 1/0

    foo()