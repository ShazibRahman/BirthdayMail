import json
import logging
import os
import pathlib

from random import choice

from Decorators.singleton import singleton_with_parameters
from Decorators.timeout_decorator import customTimeOutError, timeout
from Utils.asymetrcilaEncryDecry import decrypt
from data.images import image_list
from data.messages_list import list_of_messages

try:
    from telethon.sync import TelegramClient
except ImportError:
    print("installing dependencies")
    # print("pip install telethon")
    os.system("pip install -r requirement.txt")
    from telethon.sync import TelegramClient

time_out: int = int(os.getenv("TIMEOUTVALUE", 10))


def read_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


SESSION_PATH = (
    pathlib.Path(__file__).parent.joinpath("telegram.session").resolve().as_posix()
)


def get_message_randomly() -> str:
    return choice(list_of_messages)


@singleton_with_parameters
class Telegram:
    def __init__(self) -> None:
        print(SESSION_PATH)
        api_id: str = decrypt(os.environ.get("api_id"))
        api_hash: str = decrypt(os.environ.get("api_hash"))

        self.client = TelegramClient(
            SESSION_PATH,
            api_id,  # noqa
            api_hash,
        )

    def message(self, chat_id: str, name: str) -> None:
        if chat_id is None or chat_id == "":
            logging.error("chat id is empty")
            return
        message = get_message_randomly().format(name=name) + choice(image_list)
        logging.info(f"Sending message to {chat_id=}")
        self.client.start(os.environ["phone_number"])  # noqa
        try:
            self.client.send_message(chat_id, message)
        except Exception as e:
            logging.error(e)
        finally:
            self.client.disconnect()


@timeout(time_out)
def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%d-%b-%y %H:%M:%S",
        handlers=[logging.StreamHandler()],
    )
    logging.info("juiwufbuefbg")
    try:
        with Telegram().client:
            Telegram().message(os.environ.get("phone_number"), "Shaz NamiKaze")
    except customTimeOutError:
        logging.info(f"took more than {time_out=}")


if __name__ == "__main__":
    main()
