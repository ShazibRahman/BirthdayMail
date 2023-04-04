import argparse
import os


loggerPath = os.path.dirname(__file__) + "/logger.log"
anacron_user = "Shazib_Anacron"


def readLogs():
    os.system(f"bat --paging=never {loggerPath}")


def clearLogs():
    with open(loggerPath, "w") as file:
        pass


def cliMethod():
    if args.s == "y":
        from message import BirthdayMail

        user = os.environ.get("USER")
        working_directory = os.getcwd()
        git_dir = os.path.dirname(__file__)

        os.system(f"cd {os.path.dirname(__file__)} && git pull")

        birthday = BirthdayMail()
        birthday.logging.info(
            f"--logged in as {user=} , {__name__=} and {working_directory=}"
        )

        birthday.send_mail_from_json()
        birthday.send_email_special_occassions()
        birthday.logging.info("preparing to run git commands")
        os.system(f"cd {git_dir} && git add * ")
        os.system(f"cd {git_dir} && git commit -m 'commit'")
        os.system(f"cd {git_dir} && git push -u origin master ")
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
        from message import BirthdayMail

        birth = BirthdayMail()
        birth.get_all_bday_info()
        return
    if args.b == "a":
        from message import BirthdayMail

        birth = BirthdayMail()
        birth.get_all_bday_info(True)
        return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--logs", type=str, choices=["show", "clear"])
    parser.add_argument("-b", type=str, choices=["y", "n", "a"])
    parser.add_argument("-s", type=str, choices=["y", "n"])
    args = parser.parse_args()
    cliMethod()
