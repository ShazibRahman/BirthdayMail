import argparse
import os
import subprocess

from logger import getLogger
from message import BirthdayMail
from utils.check_internet_connectivity import check_internet_connection

loggerPath = os.path.join(os.path.dirname(__file__), "data", "logger.log")

logging = getLogger()


def read_logs(logger_path: str) -> None:
    """
    Read logs from a specified logger path.

    Args:
        logger_path (str): The path to the logger file.

    Returns:
        None
    """
    subprocess.run(["bat", "--paging=never", logger_path])


def clear_logs():
    with open(loggerPath, "w", encoding="utf-8") as file:
        file.truncate()


def cli_method(args):
    """
    Generates the function comment for the given function body in a markdown code block with the correct language syntax.

    Args:
        args (object): The command-line arguments.

    Returns:
        None: If the `args.logs` is "show" or "clear".
        None: If `args.logs` is None and `args.b` and `args.s` are also None.
        None: If `args.s` is "y" and `birthday.send_mail_from_json()` returns None.
        None: If `args.b` is not None and not an empty string.

    Raises:
        None.

    Side Effects:
        Calls various functions based on the value of `args.logs` and `args.s`.
    """
    if args.logs:
        if args.logs == "show":
            read_logs(logger_path=loggerPath)
            return
        if args.logs == "clear":
            clear_logs()
            return
    if args.logs is None and args.b is None and args.s is None:
        read_logs(logger_path=loggerPath)
        return
    if not check_internet_connection():
        logging.error("No internet connection")
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
    arg = parser.parse_args()
    cli_method(arg)
