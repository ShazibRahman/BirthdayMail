
import os

from cryptography.fernet import Fernet

from utils.load_env import load_env

# load the env file
load_env() # autopep8: off 



def get_key():
    """
    Retrieves the encryption key for the client.
    Returns:
        bytes: The encryption key encoded in UTF-8.
    """
    return os.getenv("client_ency_key").encode("utf-8")



def decrypt(env):
    """
    Decrypts the given encrypted environment variable.

    Args:
        env (str): The encrypted environment variable to decrypt.

    Returns:
        str: The decrypted environment variable.

    Raises:
        ValueError: If the decryption fails.
    """
    return Fernet(get_key()).decrypt(env.encode("utf-8")).decode("utf-8")

