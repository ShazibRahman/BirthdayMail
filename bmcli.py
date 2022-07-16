import argparse
import os

from message import BirthdayMail

loggerPath = os.path.dirname(__file__) + "/logger.log"


def readLogs():
    with open(loggerPath) as file:
        print(file.read(), end="")


def clearLogs():
    with open(loggerPath, 'w') as file:
        pass


def cliMethod():
    if args.logs is not None and args.logs == 'show':
        readLogs()
    if args.logs is not None and args.logs == 'clear':
        clearLogs()
    if args.b == "y":
        birth = BirthdayMail()
        birth.get_all_bday_info()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--logs", type=str, choices=['show', 'clear'])
    parser.add_argument("-b", type=str, choices=['y', 'n'], default='n')
    args = parser.parse_args()
    cliMethod()
