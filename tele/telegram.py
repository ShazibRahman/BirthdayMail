# pylint: disable=logging-fstring-interpolation,redefined-builtin,missing-function-docstring,unused-argument,unused-import , broad-exception-caught , wrong-import-order , wrong-import-position , missing-module-docstring
import json
import logging
import os
import pathlib
import sys
from random import choice

logger = logging.getLogger()

# autopep8: off
sys.path.append(pathlib.Path(__file__).parent.parent.resolve().as_posix())
logger.info("telegram is being imported to the main package")


from utils.asymetrcilaEncryDecry import decrypt  # noqa: E402
from utils.load_env import load_env  # noqa: E402
from decorators.timeout_decorator import TimeoutError, timeout  # noqa: E402

load_env()

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
SESSSION_PATH = (
    pathlib.Path(__file__).parent.joinpath("telegram.session").resolve().as_posix()
)


def get_message_randomly() -> str:
    return choice(MESSAGES)


class Telegram:
    """
    singleton class whose function is to create a telegram instance and send messsage to the chat
    wrote this syncronously to integrate better with the legacy code
    """

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
            api_id = decrypt(os.environ.get("api_id"))
            api_hash = decrypt(os.environ.get("api_hash"))

            self.client = TelegramClient(
                SESSSION_PATH,
                api_id,
                api_hash,
            )
        else:
            print("Telegram instance already created")

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
            Telegram().message("+91 7970502165", "Shaz NamiKaze")
    except TimeoutError:
        logging.info(f"took more than the timeout  {value=}")


if __name__ == "__main__":
    main()
