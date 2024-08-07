import socket
from functools import cache


@cache
def check_internet_connection():
    """
    Checks if there is an internet connection available by attempting to connect to a well-known website.

    Returns:
        bool: True if there is an internet connection, False otherwise.
    """
    try:
        # Connect to a well-known website
        socket.create_connection(("www.google.com", 80))
        return True
    except OSError:
        return False


if __name__ == "__main__":
    for i in range(100):
        print(check_internet_connection())
