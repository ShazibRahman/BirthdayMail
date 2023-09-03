import json
import os
import pathlib
import sys
import time
from time import sleep

#autopep8: off
sys.path.append(pathlib.Path(__file__).parent.parent.resolve().as_posix())

from utils.load_env import load_env
from utils.timeout_decorator import TimeoutError, timeout

try:
    from telethon.sync import TelegramClient
except ImportError:
    print("installing dependencies")
    # print("pip install telethon")
    os.system("pip install -r requirement.txt")
    from telethon.sync import TelegramClient

from logger import getLogger  # autopep8: off

logging = getLogger()


load_env()

value: int = int(os.getenv("TIMEOUTVALUE"))

def readJson(path: str):
    with open(path, "r") as f:
        return json.load(f)


telegram_client_secret = readJson(pathlib.Path(
    __file__).parent.joinpath("client_secret.json").resolve().as_posix())

MESSAGES: list[str] = readJson(pathlib.Path(__file__).parent.joinpath(
    "messages.json").resolve().as_posix())
SESSSION_PATH = pathlib.Path(__file__).parent.joinpath("telegram.session").resolve().as_posix()


def get_message_randomly() -> str:
    import random
    return random.choice(MESSAGES)


class Telegram:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            print("Telegram instance created")
            cls._initiated = False
        return cls._instance

    def __init__(self) -> None:
        if not self._initiated:
            self._initiated = True
            print(SESSSION_PATH)

            self.client = TelegramClient(
                SESSSION_PATH,
                telegram_client_secret["api_id"],
                telegram_client_secret["api_hash"],
            )
        else:
            print("Telegram instance already created")

    def message(self, chat_id: str, name: str) -> None:

        message = get_message_randomly().format(name=name)
        logging.info(f"Sending message to {chat_id}")
        self.client.start(telegram_client_secret["phone_number"])
        try:
            self.client.send_message(chat_id, message)
        except Exception as e:
            logging.error(e)
        finally:

            self.client.disconnect()

# @timeout(value)
def main():
    try:
        ...
    except Exception as e:
        print(e)
        try:
            with Telegram().client:
                Telegram().message("+917970502165", "Shazib")
        except TimeoutError:
            logging.info(f"took more than the timeout  {value=}")



        print("here and after")

        time.sleep(3)
        print("waited for another 3 seconds")
if __name__ == "__main__":
    main()
