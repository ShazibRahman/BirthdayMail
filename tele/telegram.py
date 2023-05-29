import asyncio
import json
import os
import pathlib
import sys
from http import client

import telethon

sys.path.append(pathlib.Path(__file__).parent.parent.resolve().as_posix())

try:
    from telethon import TelegramClient
except ImportError:
    print("installing dependencies")
    # print("pip install telethon")
    os.system("pip install -r requirement.txt")
    from telethon import TelegramClient

from logger import getLogger  # autopep8: off

logging = getLogger()


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
            asyncio.get_event_loop().run_until_complete(self.client.connect())
            if not self.client.is_connected():
                self.client.connect()
        else:
            print("Telegram instance already created")

    async def message(self, chat_id: str, name: str) -> None:

        message = get_message_randomly().format(name=name)
        logging.info(f"Sending message to {chat_id}")
        await self.client.start(telegram_client_secret["phone_number"])
        try:
            await self.client.send_message(chat_id, message)
        except Exception as e:
            logging.error(e)




if __name__ == "__main__":
    try:
        telegram = Telegram()
    except Exception as e:
        print(e)
        with Telegram().client:
            Telegram().client.loop.run_until_complete(Telegram().message("me", "test"))