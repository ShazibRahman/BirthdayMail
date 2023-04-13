import argparse
import os
from message import BirthdayMail
import subprocess
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
        response = subprocess.run(
            f"git -C {git_dir} pull", shell=True, capture_output=True
        )
        if "Already up to date." in response.stdout.decode():
            birthday.logging.info(
                f"--repository alreay up to date"
            )
        elif "Updating" in response.stdout.decode():
            birthday.logging.info(
                f"--repository updated"
            )
        elif "Changes not staged for commit" in response.stdout.decode():
            birthday.logging.info(
                f"--repository has uncommited changes"
            )
            response = subprocess.run([
                "git", "stash", "save"
            ], shell=True, capture_output=True)
            birthday.logging.info(
                f"--stashed changes"
            )
        from message import BirthdayMail
        birthday = BirthdayMail()
        birthday.get_all_bday_info()
        birthday.send_email_special_occassions()
        response = subprocess.run([
            "git", "stash", "pop"

        ])
        response = subprocess.run([
            "git", "add", "."

        ])
        if response.returncode == 0:
            birthday.logging.info(
                f"--added changes"
            )
        else:
            birthday.logging.info(
                f"--error adding changes"
            )
            birthday.git_command_failed_mail(response.stderr.decode(), "add")
        response = subprocess.run([
            "git", "commit", "-m", f"updated on {birthday.dates_done[-1]}"

        ])
        if response.returncode == 0:
            birthday.logging.info(
                f"--commited changes"
            )
        else:
            birthday.logging.info(
                f"--error committing changes"
            )
            birthday.git_command_failed_mail(
                response.stderr.decode(), "commit")
        response = subprocess.run([
            "git", "push", "origin", "master"

        ])
        if response.returncode == 0:
            birthday.logging.info(f"--pushed changes")
        else:
            birthday.logging.info(
                f"--error pushing changes"
            )
            birthday.git_command_failed_mail(response.stderr.decode(), "push")

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
