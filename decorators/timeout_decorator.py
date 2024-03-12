import signal


class TimeOutError(Exception):
    pass


def timeout(seconds):
    """
    Decorator to add a timeout to a function.

    Parameters:
        seconds (int): The number of seconds before the function times out.

    Returns:
        wrapper: The decorated function with a timeout.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            def handler(signum, frame):
                raise TimeOutError("Function execution exceeded the specified timeout.")

            # Set up a signal handler to raise TimeoutError if the timeout is reached
            signal.signal(signal.SIGALRM, handler)
            # Schedule the alarm to trigger in 'seconds' seconds
            signal.alarm(seconds)

            try:
                result = func(*args, **kwargs)  # Call the original function
            finally:
                # Cancel the alarm if the function returns or an exception is raised
                signal.alarm(0)

            return result

        return wrapper

    return decorator
