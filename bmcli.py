import argparse
import os

from message import BirthdayMail

loggerPath = os.path.dirname(__file__) + "/logger.log"


def readLogs():
    os.system(f"bat --paging=never {loggerPath}")


def clearLogs():
    with open(loggerPath, "w") as file:
        pass


def cliMethod():
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
        birth = BirthdayMail()
        birth.get_all_bday_info()
        return
    if args.b == "a":
        birth = BirthdayMail()
        birth.get_all_bday_info(True)
        return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--logs", type=str, choices=["show", "clear"])
    parser.add_argument("-b", type=str, choices=["y", "n", "a"])
    args = parser.parse_args()
    cliMethod()
