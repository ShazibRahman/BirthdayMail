import json
import os
import pathlib
import sys

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
            self.client = TelegramClient(
                "telegram",
                telegram_client_secret["api_id"],
                telegram_client_secret["api_hash"],
            )
        else:
            print("Telegram instance already created")

    async def message(self, chat_id: str, name: str) -> None:

        message = get_message_randomly().format(name=name)
        await self.client.start(telegram_client_secret["phone_number"])
        try:
            await self.client.send_message(chat_id, message)
        except Exception as e:
            logging.error(e)
        finally:
            await self.client.disconnect()

        


if __name__ == "__main__":
    with Telegram().client:
        Telegram().client.loop.run_until_complete(
            Telegram().message("+91 79705 02165", "shazib"))
