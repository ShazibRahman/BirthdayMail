import argparse
import os
import subprocess

from logger import getLogger
from message import BirthdayMail

loggerPath = os.path.join(os.path.dirname(__file__), "data", "logger.log")

logging = getLogger()


def read_logs():
    subprocess.run(["bat", "--paging=never", loggerPath])


def clear_logs():
    open(loggerPath, "w").close()


def cli_method():
    if args.logs and args.logs == "show":
        read_logs()
        return
    if args.logs and args.logs == "clear":
        clear_logs()
        return
    if args.logs is None and args.b is None and args.s is None:
        read_logs()
        return
    birthday = BirthdayMail()

    if args.s == "y":
        if birthday.send_mail_from_json() is None:
            logging.info("Exiting...")
            exit(0)

        birthday.send_email_special_occassions()
        birthday.upload()

        return

    if args.b is not None and args.b != "":
        birthday.get_all_bday_info(args.b)
        return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--logs", type=str, choices=["show", "clear"])
    parser.add_argument("-b", type=str)
    parser.add_argument("-s", type=str, choices=["y", "n"])
    args = parser.parse_args()
    cli_method()
