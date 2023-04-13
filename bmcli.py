import argparse
import os
from message import BirthdayMail
birthday = BirthdayMail()


loggerPath = os.path.join(os.path.dirname(__file__), "logger.log")
anacron_user = "Shazib_Anacron"
git_dir = os.path.dirname(__file__)


def readLogs():
    os.system(f"bat --paging=never {loggerPath}")


def clearLogs():
    with open(loggerPath, "w") as _:
        pass


def cliMethod():
    if args.s == "y":

        user = os.environ.get("USER")

        birthday.logging.info(
            f"--logged in as {user=}"
        )

        birthday.send_mail_from_json()
        birthday.send_email_special_occassions()

        return
    if args.logs is not None and args.logs == "show":
        readLogs()
        return
    if args.logs is not None and args.logs == "clear":
        clearLogs()
        return
    if args.logs is None and args.b is None:
        readLogs()
        return
    if args.b == "y":
        birthday.get_all_bday_info()
        return
    if args.b == "a":
        birthday.get_all_bday_info(True)
        return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--logs", type=str, choices=["show", "clear"])
    parser.add_argument("-b", type=str, choices=["y", "n", "a"])
    parser.add_argument("-s", type=str, choices=["y", "n"])
    args = parser.parse_args()
    cliMethod()
