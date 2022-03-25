import argparse
import os

loggerPath = os.path.dirname(__file__) + "/logger.log"


def readLogs():
    with open(loggerPath) as file:
        print(file.read())


def clearLogs():
    with open(loggerPath, 'w') as file:
        pass


def cliMethod():
    if args.logs is not None and args.logs == 'show':
        readLogs()
    if args.logs is not None and args.logs == 'clear':
        clearLogs()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--logs", type=str, choices=['show', 'clear'])
    args = parser.parse_args()
    cliMethod()
