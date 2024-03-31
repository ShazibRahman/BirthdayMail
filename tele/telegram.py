import json
import logging
import os
import pathlib
from random import choice

from Decorators.singleton import singleton_with_parameters
from Decorators.timeout_decorator import TimeOutError, timeout
from Utils.asymetrcilaEncryDecry import decrypt
from Utils.load_env import load_env

load_env()

logger = logging.getLogger()

try:
    from telethon.sync import TelegramClient
except ImportError:
    print("installing dependencies")
    # print("pip install telethon")
    os.system("pip install -r requirement.txt")
    from telethon.sync import TelegramClient

value: int = int(os.getenv("TIMEOUTVALUE"))


def read_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


MESSAGES: list[str] = read_json(
    path=pathlib.Path(__file__).parent.joinpath("messages.json").resolve().as_posix()
)
SESSION_PATH = (
    pathlib.Path(__file__).parent.joinpath("telegram.session").resolve().as_posix()
)


def get_message_randomly() -> str:
    return choice(MESSAGES)


@singleton_with_parameters
class Telegram:
    def __init__(self) -> None:
        print(SESSION_PATH)
        api_id = decrypt(os.environ.get("api_id"))
        api_hash = decrypt(os.environ.get("api_hash"))

        self.client = TelegramClient(
            SESSION_PATH,
            api_id,
            api_hash,
        )

    def message(self, chat_id: str, name: str) -> None:
        if chat_id is None or chat_id == "":
            logging.error("chat id is empty")
            return
        message = get_message_randomly().format(name=name)
        logging.info(f"Sending message to {chat_id}")
        self.client.start(os.environ["phone_number"])
        try:
            self.client.send_message(chat_id, message)
        except Exception as e:
            logging.error(e)
        finally:
            self.client.disconnect()


@timeout(value)
def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%d-%b-%y %H:%M:%S",
        handlers=[logging.StreamHandler()],
    )
    try:
        with Telegram().client:
            logging.info("I am here")
            Telegram().message(os.environ.get("phone_number"), "Shaz NamiKaze")
    except TimeOutError:
        logging.info(f"took more than the timeout  {value=}")


if __name__ == "__main__":
    main()
