import argparse
import os
import subprocess
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
        pull_return = subprocess.run(
            f"git -C {git_dir} pull", shell=True, capture_output=True)
        if pull_return.returncode != 0:
            birthday.logging.info(
                f"git pull failed with return code {pull_return}"
            )
            birthday.git_command_failed_mail(
                pull_return.stderr.decode(), "pull")
            return

        birthday.send_mail_from_json()
        birthday.send_email_special_occassions()
        add_return = subprocess.run(
            f"git -C {git_dir} add .", shell=True, capture_output=True)
        if add_return.returncode != 0:
            birthday.logging.info(
                f"git add failed with return code {add_return}"
            )
            birthday.git_command_failed_mail(
                add_return.stderr.decode(), "add")
            return
        commit_return = subprocess.run(
            f"git -C {git_dir} commit -m 'auto commit'", shell=True, capture_output=True)
        if commit_return.returncode != 0:
            birthday.logging.info(
                f"git commit failed with return code {commit_return}"
            )
            birthday.git_command_failed_mail(
                commit_return.stderr.decode(), "commit")
            return
        push_return = subprocess.run(
            f"git -C {git_dir} push", shell=True, capture_output=True)
        if push_return.returncode != 0:
            birthday.logging.info(
                f"git push failed with return code {push_return}"
            )
            birthday.git_command_failed_mail(
                push_return.stderr.decode(), "push")
            return
        birthday.logging.info(f"git push successful")
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
