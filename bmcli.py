import argparse
import os
from message import BirthdayMail
birthday = BirthdayMail()

try:
    from git import Repo
except:
    birthday.logging.info("GitPython not installed")
    birthday.logging.info("Installing GitPython")
    birthday.logging.info("Please wait...")
    birthday.logging.info("This may take a while")
    if os.name == "posix":
        os.system("pip3 install gitpython")
    else:
        os.system("pip install gitpython")
    from git import Repo
    birthday.logging.info("GitPython installed successfully")


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
        repo = Repo(git_dir)
        if repo.remotes.origin.url == "":
            birthday.logging.info("No remote url found")
            birthday.logging.info("Please add remote url")
            birthday.logging.info("Aborting...")
            return
        if repo.is_dirty():
            birthday.logging.info("--repo is dirty--")
            repo.git.stash('save')
            birthday.logging.info("--stashed changes--")

        birthday.logging.info("--checking for updates--")

        try:
            repo.remotes.origin.pull()
            birthday.logging.info("--update successful--")

        except Exception as e:
            birthday.logging.info("--update failed--", str(e))
            birthday.logging.info("Aborting...")
            birthday.git_command_failed_mail(str(e), "pull")
            return
        finally:
            if repo.is_dirty():
                repo.git.stash('apply')
                birthday.logging.info("--popped changes--")
                repo.git.add(".")
                repo.git.commit("-m", "Update")
                repo.remotes.origin.push()

        birthday.send_mail_from_json()
        birthday.send_email_special_occassions()

        birthday.logging.info("--pushing changes--")
        try:
            repo.git.add(".")
            repo.git.commit("-m", "Update")
            repo.remotes.origin.push()
            birthday.logging.info("--push successful--")
        except Exception as e:
            birthday.logging.info("--push failed--")
            birthday.logging.info("Aborting...")
            birthday.git_command_failed_mail(str(e), "push")
            return

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
