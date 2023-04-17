import json
import ssl
import smtplib
import logging
import time
import os
import random
from typing import Tuple
from email.message import EmailMessage
from datetime import datetime, timedelta
from gdrive.GDrive import GDrive

try:
    from jinja2 import Template

except ImportError:
    if os.name == "nt":
        os.system("pip install -r requirement.txt")
    else:
        os.system("pip3 install -r requirement.txt")
    from jinja2 import Template


logger_path = os.path.join(os.path.dirname(__file__), "logger.log")

if not os.path.exists(logger_path):
    with open(logger_path, "w") as f:
        pass

logging.basicConfig(
    filename=logger_path,
    filemode="a",
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
)

ctx = ssl.create_default_context()
ctx.verify_mode = ssl.CERT_REQUIRED
anacron_user = "Shazib_Anacron"


def convert(seconds):
    return time.strftime("%H hours %M Minutes %S Seconds to go ", time.gmtime(seconds))


def render_template(template: Template, context: dict):
    return template.render(context)


def saveJsontoFile(fileName: str, data: list, indent: int = 4) -> None:
    with open(fileName, "w") as f:
        json.dump(data, f, indent=indent)
    logging.info(f"write changes to {fileName=}")


def read_json_to_py_objecy(fileName: str):
    with open(fileName) as f:
        return json.load(f)


def find_next_leap_year(year: int) -> int:
    if year % 4 == 0 and year % 100 != 0 or year % 400 == 0:
        return year + 4
    elif year % 4 != 0:
        return year + year % 4
    elif year % 4 == 0 and year % 100 == 0 or year % 400 != 0:
        return year + 4
    else:
        return year


def isLeapYear(year: int) -> bool:
    return year % 4 == 0 and year % 100 != 0 or year % 400 == 0


def isGreater(day1: int, month1: int, day2: int, month2: int) -> bool:
    if month1 > month2:
        return True
    elif month1 == month2 and day1 > day2:
        return True
    else:
        return False


def send_mail(sender_email: str, password: str, message: EmailMessage):
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ctx) as server:
            server.login(sender_email, password)
            server.send_message(message)
    except Exception as e:
        logging.error("---Network Error---", str(e))
        return False
    return True


class BirthdayMail:
    def __init__(self) -> None:

        logging.info("----Starting the application----")
        self.logging = logging

        self.template_filename = None
        self.template_to_render = None
        self.directoryString = os.path.dirname(__file__)
        self.sender_email: str = os.environ.get("shazmail")  # type: ignore
        self.password: str = os.environ.get("shazPassword")  # type: ignore
        user = os.environ.get("USER")

        logging.info(
            f"--logged in as {user=}"
        )

        self.formatString = "%d-%m"
        self.formatStringWithYear = "%d-%m-%Y"
        self.format_late_mail_date = "%d-%b"
        self.occasion_path = os.path.join(self.directoryString,
                                          "occasions.json")
        self.data_path = os.path.join(self.directoryString, "data.json")

    def sendEmailOnSpecialOccasion(self, Occasion: dict):
        template_filename = os.path.join(
            self.directoryString, "templates", Occasion["template"]
        )

        self.template_to_render = Template(open(template_filename).read())
        context_template = render_template(self.template_to_render, {})
        if len(Occasion["peopleToGreet"]) <= 0:
            logging.info(
                f"No Person is found in the occasions {Occasion['name']}")

        for person in Occasion["peopleToGreet"]:
            message = EmailMessage()
            message["Subject"] = (
                Occasion["subject"] + " " + person["name"].split("(")[0] + "!"
            )
            message["From"] = self.sender_email
            message["To"] = person["mail"]

            message.set_content(context_template, subtype="html")
            if send_mail(self.sender_email, self.password, message):
                logging.info(
                    f"The email has been sent to {person['name']} with email {person['mail']} using template {Occasion['template']}"
                )
            else:
                exit(1)

            Occasion["peopleToGreet"].remove(person)

    def message_func(self, val: dict, pending_mail=False) -> bool:
        receiver_email = val["mail"]
        name = val["name"]
        message = EmailMessage()
        message["Subject"] = "Happy Birthday " + name.split("(")[0]
        message["From"] = self.sender_email
        message["To"] = receiver_email

        if pending_mail:
            templaneName = "late.html"
        else:
            templateList = ["template_3.html",
                            "template_2.html",
                            "template_1.html"]
            templaneName = random.choice(templateList)
        self.template_filename = os.path.join(
            self.directoryString, "templates", templaneName)
        self.template_to_render = Template(open(self.template_filename).read())
        context_template = render_template(
            self.template_to_render, {"name": name})

        message.set_content(context_template, subtype="html")
        return send_mail(self.sender_email, self.password, message)

    def check_for_pending_and_send_message(self):

        if not self.dates_done or len(self.dates_done) <= 0:
            logging.info("--No Previous date found--")
            return True

        current_datetime, _ = self.get_current_date()
        self.sort_date_dones_files()

        last_run_datetime = datetime.strptime(
            self.dates_done[-1], self.formatStringWithYear
        )

        modified_dates_file = False

        current_datetime = datetime.strptime(
            current_datetime.strftime(self.formatStringWithYear),
            self.formatStringWithYear,
        )  # to make datetime format same as the one last_run_date

        if last_run_datetime == current_datetime - timedelta(1):
            return True
        else:
            last_run = last_run_datetime + timedelta(1)
            last_run_set: set[str] = set()
            last_run_with_year_set = set()

            while last_run < current_datetime:
                last_run_string = last_run.strftime(self.formatString)
                last_run_set.add(last_run_string)
                last_run_with_year_set.add(
                    last_run.strftime(self.formatStringWithYear)
                )
                last_run = last_run + timedelta(1)

            dates_list = [
                datetime.strptime(x, self.formatString).strftime(
                    self.format_late_mail_date
                )
                for x in last_run_set
            ]

            logging.info(f"--trying to send backlog emails for {dates_list=}")

            for val in self.bday:
                if val["date"] in last_run_set:
                    logging.info(
                        f"--trying backlog mail dated={val['date']} for email={val['mail']}")
                    success = self.message_func(val, True)
                    if success:
                        logging.info(
                            f"Backlog email for date {val['date']} and email {val['mail']} has been sent"
                        )

                    else:
                        return False
            for i in last_run_with_year_set:
                self.dates_done.append(i)
                modified_dates_file = True

        if modified_dates_file:
            self.sort_date_dones_files()
            saveJsontoFile(os.path.join(self.directoryString,
                           "dates.json"), self.dates_done)
        return True

    def send_mail_from_json(self):
        self.dates_done: list[str] = json.load(
            open(os.path.join(self.directoryString, "dates.json"))
        )
        current_date_time, current_date_withyear = self.get_current_date()
        if current_date_withyear in self.dates_done:
            logging.info(
                f"script for {current_date_withyear} has already been executed"
            )
            exit(1)
        self.gdrive = GDrive()
        if self.download():
            self.dates_done = json.load(
                open(os.path.join(self.directoryString, "dates.json"))
            )
            current_date_time, current_date_withyear = self.get_current_date()
            if current_date_withyear in self.dates_done:
                logging.info(
                    f"script for {current_date_withyear} has already been executed"
                )
                exit(1)
        current_time = current_date_time.strftime(self.formatString)
        self.bday: dict = json.load(open(self.data_path))

        prev_success = self.check_for_pending_and_send_message()

        if not prev_success:
            logging.info("---Sending Backlog email failed---")
            exit(1)

        match: bool = False
        success: bool = False
        modified_dates_done_file = False

        for val in self.bday:
            if current_time == val["date"]:
                success = self.message_func(val)
                match = True

        if match and success:
            self.dates_done.append(current_date_withyear)
            modified_dates_done_file = True

        if not match:
            modified_dates_done_file = True
            logging.info("--None has birthday today--")
            self.dates_done.append(current_date_withyear)

        if modified_dates_done_file:
            self.sort_date_dones_files()
            saveJsontoFile(os.path.join(self.directoryString,
                           "dates.json"), self.dates_done)

    def get_current_date(self) -> Tuple[datetime, str]:
        current_date_time = datetime.now()
        current_date_withyear = current_date_time.strftime(
            self.formatStringWithYear)

        return current_date_time, current_date_withyear

    def sort_date_dones_files(self) -> None:
        # remove duplicates
        self.dates_done = list(set(self.dates_done))
        self.dates_done.sort(
            key=lambda x: datetime.strptime(x, self.formatStringWithYear)
        )

    def send_email_special_occassions(self):
        _, current_date_withyear = self.get_current_date()

        self.occasions: list = json.load(
            open(self.occasion_path))

        for Occasion in self.occasions:
            if current_date_withyear == Occasion["date"]:
                self.sendEmailOnSpecialOccasion(Occasion)
                saveJsontoFile(self.occasion_path, self.occasions)
            else:
                logging.info("--No Special occasion today")

    def get_all_bday_info(self, print_all: bool = False):
        self.bday: dict = json.load(
            open(self.data_path))
        lis = []
        for val in self.bday:
            next_birthday, diff_datetime = self.count_down_for_birthday(
                val["date"])

            parse_date_to_look_good = datetime.strftime(
                next_birthday, "%d %b %Y")
            days_rem_mes = f"{diff_datetime.days} days {convert(diff_datetime.seconds)}"

            lis.append(
                [diff_datetime.days, val["name"],
                    parse_date_to_look_good, days_rem_mes]
            )
        lis.sort()
        if not print_all:
            lis = lis[:3]

        for l, i, j, k in lis:
            print(i, j, k, end="\n\n", sep="\n")

    def nextBirthYear(self, birthdayString: str) -> int:
        day1, month1 = birthdayString.split("-")
        today = datetime.now()
        day2, month2, year = today.day, today.month, today.year
        if month1 == "02" and day1 == "29":
            if isGreater(int(day1), int(month1), day2, month2) and isLeapYear(year):
                return year
            else:
                return find_next_leap_year(year)

        elif isGreater(int(day1), int(month1), day2, month2):
            return year
        else:
            return year + 1

    def count_down_for_birthday(
        self, birthdayString: str
    ) -> tuple[datetime, timedelta]:
        today = datetime.now()
        birthdayString = birthdayString + "-" + \
            str(self.nextBirthYear(birthdayString))
        birthday_ = datetime.strptime(
            birthdayString, self.formatStringWithYear)
        return birthday_, birthday_ - today

    def git_command_failed_mail(self, body: str, subject: str = "Git Command Failed") -> None:
        if ("Your branch is up to date" in body) or ("nothing to commit" in body):
            return
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = self.sender_email
        message["To"] = self.sender_email
        message.set_content(body)
        send_mail(self.sender_email, self.password, message)

    def download(self):
        return self.gdrive.download()

    def upload(self):
        return self.gdrive.upload()


if __name__ == "__main__":
    user = os.environ.get("USER")
    working_directory = os.getcwd()
    birthday = BirthdayMail()
    logging.info(
        f"--logged in as {user=} , {__name__=} and {working_directory=}")

    birthday.send_mail_from_json()
    birthday.send_email_special_occassions()
