
import os

from cryptography.fernet import Fernet

from utils.load_env import load_env

# load the env file
load_env() # autopep8: off 



def get_key():
    return os.getenv("client_ency_key").encode("utf-8")


def decrypt(env):
    return Fernet(get_key()).decrypt(env.encode("utf-8")).decode("utf-8")
