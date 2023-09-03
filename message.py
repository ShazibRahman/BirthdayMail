# autopep8: off
import json
import os
import random
import smtplib
import ssl
import sys
import time
from datetime import datetime, timedelta
from email.message import EmailMessage
from http import client
from re import T
from typing import Literal, Tuple

from typing_extensions import deprecated

from logger import getLogger
from tele.telegram import Telegram
from utils.csv_to_json import main as csv_to_json
from utils.load_env import load_env
from utils.time_it import timeit
from utils.timeout_decorator import TimeoutError, timeout

load_env()

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
# noinspection PyUnresolvedReferences
from gdrive.GDrive import GDrive  # noqa: E402

try:
    from jinja2 import Template

except ImportError:
    if os.name == "nt":
        os.system("pip install -r requirement.txt")
    else:
        os.system("pip3 install -r requirement.txt")
    from jinja2 import Template

logging = getLogger()

anacron_user = "Shazib_Anacron"
FOLDER_NAME = "BirthDayMail"
timeout_value = int(os.getenv("TIMEOUTVALUE"))


def convert(seconds):
    return time.strftime("%H hours %M Minutes %S Seconds to go ", time.gmtime(seconds))


def render_template(template: Template, context: dict):
    return template.render(context)


@timeit
def save_jsonto_file(file_name: str, data: list, indent: int = 4) -> None:
    with open(file_name, "w") as f:
        json.dump(data, f, indent=indent)
    logging.info(f"write changes to {file_name=}")


@timeit
def read_json_to_py_objecy(file_name: str):
    with open(file_name) as f:
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


def is_leap_year(year: int) -> bool:
    return year % 4 == 0 and year % 100 != 0 or year % 400 == 0


def is_greater(day1: int, month1: int, day2: int, month2: int) -> bool:
    if month1 > month2:
        return True
    elif month1 == month2 and day1 > day2:
        return True
    else:
        return False


@timeit
def send_mail(sender_email: str, password: str, message: EmailMessage):
    ctx = ssl.create_default_context()
    ctx.verify_mode = ssl.CERT_REQUIRED
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ctx) as server:
            server.login(sender_email, password)
            server.send_message(message)
            logging.info(f"---Mail sent to {message['To']}---")
    except Exception as e:
        logging.error("---Network Error---" + str(e))
        return False
    return True


def next_birth_year(birthday_string: str) -> int:
    day1, month1 = birthday_string.split("-")
    today = datetime.now()
    day2, month2, year = today.day, today.month, today.year
    if month1 == "02" and day1 == "29":
        if is_greater(int(day1), int(month1), day2, month2) and is_leap_year(year):
            return year
        else:
            return find_next_leap_year(year)

    elif is_greater(int(day1), int(month1), day2, month2):
        return year
    else:
        return year + 1


class BirthdayMail:
    def __init__(self) -> None:

        self.occasions = None
        self.bday = None
        self.dates_done = None
        logging.info("----Starting the application----")
        self.logging = logging

        self.template_filename = None
        self.template_to_render = None
        self.directory_string = os.path.dirname(__file__)
        self.sender_email: str = os.environ.get("shazmail")  # type: ignore
        self.password: str = os.environ.get("shazPassword")  # type: ignore
        user = os.environ.get("USER")

        logging.info(
            f"--logged in as {user=}"
        )

        self.format_string = "%d-%m"
        self.format_string_with_year = "%d-%m-%Y"
        self.format_late_mail_date = "%d-%b"
        self.occasion_path = os.path.join(self.directory_string, "data",
                                          "occasions.json")
        self.data_path = os.path.join(
            self.directory_string, "data", "data.json")
        self.dates_done_path = os.path.join(self.directory_string, "data",
                                            "dates.json")

    def send_email_on_special_occasion(self, occasion: dict):
        template_filename = os.path.join(
            self.directory_string, "templates", occasion["template"]
        )

        self.template_to_render = Template(open(template_filename).read())
        context_template = render_template(self.template_to_render, {})
        if len(occasion["peopleToGreet"]) <= 0:
            logging.info(
                f"No Person is found in the occasions {occasion['name']}")

        for person in occasion["peopleToGreet"]:
            message = EmailMessage()
            message["Subject"] = (
                    occasion["subject"] + " " + person["name"].split("(")[0] + "!"
            )
            message["From"] = self.sender_email
            message["To"] = person["mail"]

            message.set_content(context_template, subtype="html")
            if send_mail(self.sender_email, self.password, message):
                logging.info(
                    f"The email has been sent to {person['name']} with email {person['mail']} using template {occasion['template']}"
                )

            # occasion["peopleToGreet"].remove(person) it is not very good to remove the person from the list that is
            # being iterated over

    def message_func(self, val: dict, pending_mail=False) -> bool:
        receiver_email = val["mail"]
        name = val["name"]
        message = EmailMessage()
        message["Subject"] = "Happy Birthday " + name.split("(")[0]
        message["From"] = self.sender_email
        message["To"] = receiver_email

        if pending_mail:
            template_name = "late.html"
        else:
            template_list = ["template_3.html",
                             "template_2.html",
                             "template_1.html"]
            template_name = random.choice(template_list)
        self.template_filename = os.path.join(
            self.directory_string, "templates", template_name)
        self.template_to_render = Template(open(self.template_filename).read())
        context_template = render_template(
            self.template_to_render, {"name": name})

        message.set_content(context_template, subtype="html")
        return send_mail(self.sender_email, self.password, message)

    @timeit
    def check_for_pending_and_send_message(self):

        if not self.dates_done or len(self.dates_done) <= 0:
            logging.info("--No Previous date found--")
            return True

        current_datetime, _ = self.get_current_date()
        self.sort_date_dones_files()

        last_run_datetime = datetime.strptime(
            self.dates_done[-1], self.format_string_with_year
        )

        modified_dates_file = False

        current_datetime = datetime.strptime(
            current_datetime.strftime(self.format_string_with_year),
            self.format_string_with_year,
        )  # to make datetime format same as the one last_run_date

        if last_run_datetime == current_datetime - timedelta(1):
            return True
        else:
            last_run = last_run_datetime + timedelta(1)
            last_run_set: set[str] = set()
            last_run_with_year_set = set()

            while last_run < current_datetime:
                last_run_string = last_run.strftime(self.format_string)
                last_run_set.add(last_run_string)
                last_run_with_year_set.add(
                    last_run.strftime(self.format_string_with_year)
                )
                last_run = last_run + timedelta(1)

            dates_list = [
                datetime.strptime(x, self.format_string).strftime(
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
                        self.send_telegram()
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
            save_jsonto_file(self.dates_done_path, self.dates_done)
        return True

    @timeit
    def send_mail_from_json(self):
        self.dates_done: list[str] = json.load(
            open(self.dates_done_path)
        )
        current_date_time, current_date_withyear = self.get_current_date()
        if current_date_withyear in self.dates_done:
            logging.info(
                f"script for {current_date_withyear} has already been executed"
            )
            return None
        if self.download():
            self.dates_done = json.load(
                open(file=self.dates_done_path)
            )
            if current_date_withyear in self.dates_done:
                logging.info(
                    f"script for {current_date_withyear} has already been executed"
                )
                return None
        current_time = current_date_time.strftime(self.format_string)
        self.download_read_csv_from_server_then_upload()
        self.bday: dict = json.load(open(self.data_path))

        prev_success = self.check_for_pending_and_send_message()

        if not prev_success:
            logging.info("---Sending Backlog email failed---")
            return None

        match: bool = False
        success: bool = False
        modified_dates_done_file = False

        for val in self.bday:
            if current_time == val["date"]:
                success = self.message_func(val)
                if success:
                    self.send_telegram(val['mobile'],val['name'])
                    logging.info(
                        f"email for date {val['date']} and email {val['mail']} has been sent"
                    )
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
            save_jsonto_file(self.dates_done_path, self.dates_done)
        return True

    def get_current_date(self) -> Tuple[datetime, str]:
        current_date_time = datetime.now()
        current_date_withyear = current_date_time.strftime(
            self.format_string_with_year)

        return current_date_time, current_date_withyear

    def sort_date_dones_files(self) -> None:
        # remove duplicates
        self.dates_done = list(set(self.dates_done))
        self.dates_done.sort(
            key=lambda x: datetime.strptime(x, self.format_string_with_year)
        )

    def send_email_special_occassions(self):
        _, current_date_withyear = self.get_current_date()

        self.occasions: list = json.load(
            open(self.occasion_path))

        for occasion in self.occasions:
            if current_date_withyear == occasion["date"] or ('sent' in occasion and not occasion["sent"]):
                self.send_email_on_special_occasion(occasion)
                occasion["sent"] = True
                save_jsonto_file(self.occasion_path, self.occasions)
            else:
                logging.info("--No Special occasion today")

    def get_all_bday_info(self, print_num: str = "a"):
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
        if print_num != "a":
            lis = lis[:int(print_num)]

        for _, i, j, k in lis:
            print(i, j, k, end="\n\n", sep="\n")

    def count_down_for_birthday(
            self, birthday_string: str
    ) -> tuple[datetime, timedelta]:
        today = datetime.now()
        birthday_string = birthday_string + "-" + \
                          str(next_birth_year(birthday_string))
        birthday_ = datetime.strptime(
            birthday_string, self.format_string_with_year)
        return birthday_, birthday_ - today

    def telegram_session_error(self, body: str, subject: str = "session error") -> None:
        if ("Your branch is up to date" in body) or ("nothing to commit" in body):
            return
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = self.sender_email
        message["To"] = self.sender_email
        message.set_content(body)
        send_mail(self.sender_email, self.password, message)

    @timeit
    def download(self):
        return GDrive(FOLDER_NAME, logging).download(self.dates_done_path)

    @timeit
    def upload(self):
        return GDrive(FOLDER_NAME, logging).upload(self.dates_done_path)

    @timeit
    def download_read_csv_from_server_then_upload(self):
        GDrive(FOLDER_NAME, logging).download(self.data_path)
        csv_to_json()
        GDrive(FOLDER_NAME, logging).upload(self.data_path)

    @timeit
    @timeout(10)
    @deprecated
    def check_if_session_connection(self) -> Literal[True]:
        return True


    @timeit
    @timeout(timeout_value)

    def send_telegram(self, chat_id, name):
        error = False
        logging.info("trying to send telegram message")
        try:
            with Telegram().client:
                Telegram().message(chat_id, name)
        except TimeoutError:
            logging.error(f"sending message to {name} failed due to authentication timeout")
            error = True
            self.telegram_session_error(body="Telegram authentication failed",subject="please re-login again")
        if not error:
            self.logging.info(f"telegram message sent to {name}")








if __name__ == "__main__":
    birthday = BirthdayMail()

    if birthday.send_mail_from_json() is None:
        logging.info("exiting")
        exit(0)
    birthday.send_email_special_occassions()
    birthday.upload()
