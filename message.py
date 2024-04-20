import base64
import json
import logging
import os
import pathlib
import random
import smtplib
import ssl
import sys
import time
from datetime import datetime, timedelta
from email.message import EmailMessage
from functools import lru_cache
from typing import Literal, Tuple

from Decorators.deprecated import deprecated
from Decorators.retry import retry
from Decorators.time_it import timeit
from Decorators.timeout_decorator import customTimeOutError, timeout
from Utils.DesktopNotification import DesktopNotification
from Utils.check_internet_connectivity import check_internet_connection
from Utils.csv_to_json import main as csv_to_json
from Utils.lock_manager import LockManager
from gdrive.GDrive import GDrive
from telegram.telegram import Telegram

pwd = pathlib.Path(__file__).parent.resolve()

try:
    from jinja2 import Template

except ImportError:
    if os.name == "nt":
        os.system("pip install -r requirement.txt")
    else:
        os.system("pip3 install -r requirement.txt")
    from jinja2 import Template

logger = logging.getLogger()

FOLDER_NAME = "BirthDayMail"
timeout_value = int(os.getenv("TIMEOUTVALUE","10"))


def convert(seconds: int) -> str:
    return time.strftime("%H hours %M Minutes %S Seconds to go ", time.gmtime(seconds))


def get_encoded_image_string(path: str | pathlib.Path) -> str:
    with open(path, "rb") as f:
        image_data = f.read()
        base64_encoded_image_string = base64.b64encode(image_data).decode("utf-8")
        print(base64_encoded_image_string)
        return base64_encoded_image_string


def render_template(template: Template, context: dict) -> str:
    img_folder = os.path.join(pwd, "data", "image")

    images = os.listdir(img_folder)
    images = [img for img in images if 'icon' not in img]
    random.shuffle(images)
    image = random.choice(images)
    context["image"] = f"data:image/png;base64,{get_encoded_image_string(os.path.join(img_folder, image))}"

    return template.render(context)


@timeit
def save_json_file(file_name: str, data: list, indent: int = 4) -> None:
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent)
    logging.info(f"write changes to {file_name=}")


@timeit
def read_json_to_py_object(file_name: str):
    with open(file_name, encoding="utf-8") as f:
        return json.load(f)


def find_next_leap_year(year: int) -> int:
    if year % 4 == 0 and year % 100 != 0 or year % 400 == 0:
        return year + 4
    elif year % 4 != 0:
        return year + year % 4
    else:
        return year + 4


def is_leap_year(year: int) -> bool:
    return year % 4 == 0 and year % 100 != 0 or year % 400 == 0


def is_greater(day1: int, month1: int, day2: int, month2: int) -> bool:
    return month1 > month2 or month1 == month2 and day1 > day2


@timeit
def send_mail(sender_email: str, password: str, message: EmailMessage) -> bool:
    ctx: ssl.SSLContext = ssl.create_default_context()
    ctx.verify_mode = ssl.CERT_REQUIRED
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ctx) as server:
            server.login(sender_email, password)
            server.send_message(message)
            logging.info(f"---Mail sent to {message['To']}---")
    except Exception as e:
        logging.error(f"---Network Error---{repr(e)}")
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


lock_file = os.path.join(os.path.dirname(__file__), "lock.lock")

lock_manager = LockManager(lock_file)


class BirthdayMail:
    def __init__(self) -> None:
        """
        Initializes the class and sets up the necessary instance variables.

        :param None

        :return None
        """

        if not lock_manager.acquire_control():
            sys.exit(1)

        self.bday = None
        self.dates_done = None
        logging.info("----Starting the application----")
        self.logging = logging

        self.template_filename = None
        self.template_to_render = None
        self.directory_string = os.path.dirname(__file__)
        self.sender_email: str = os.environ.get("shazmail")  # type: ignore
        self.password: str = os.environ.get("shazPassword")  # type: ignore
        if user := (os.environ.get("USER")):
            logging.info(f"--logged in as {user=}")

        self.format_string = "%d-%m"
        self.format_string_with_year = "%d-%m-%Y"
        self.format_late_mail_date = "%d-%b"

        self.data_path = pathlib.Path(self.directory_string).joinpath("data", "data.json")
        self.dates_done_path = pathlib.Path(self.directory_string).joinpath("data", "dates.json")

    def __del__(self):
        """
        Releases the lock.
        """
        lock_manager.release_control()

    def message_func(self, val: dict, pending_mail=False) -> bool:
        receiver_email = val["mail"]
        name = val["name"]
        message = EmailMessage()
        message["Subject"] = "Happy Birthday " + name.split("(")[0]
        message["From"] = self.sender_email
        message["To"] = receiver_email

        if pending_mail:
            template_name = "late.html"
            self.template_filename = os.path.join(
                self.directory_string, "templates", template_name
            )
        else:
            template_list = os.listdir(
                os.path.join(self.directory_string, "templates", "bday_templates")
            )
            random.shuffle(template_list)
            template_name = random.choice(template_list)
        self.template_filename = os.path.join(
            self.directory_string, "templates", "bday_templates", template_name
        )
        self.template_to_render = Template(
            open(self.template_filename, encoding="utf-8").read()
        )
        context_template = render_template(self.template_to_render, {"name": name})

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
            return True  # returning true as there is no pending mail
        last_run = last_run_datetime + timedelta(1)
        last_run_set: set[str] = set()
        last_run_with_year_set = set()

        while last_run < current_datetime:
            # preparing a set of dates from today -1 to last_run +1 to send pending mails
            last_run_string = last_run.strftime(self.format_string)
            last_run_set.add(last_run_string)
            last_run_with_year_set.add(last_run.strftime(self.format_string_with_year))
            last_run = last_run + timedelta(1)  # to get the next date

        dates_list = [
            datetime.strptime(x, self.format_string).strftime(
                self.format_late_mail_date
            )
            for x in last_run_set
        ]

        logging.info(f"--trying to send backlog emails for {dates_list=}")

        for val in self.bday:
            # not we are looping over pending dates to see if there is any birthday mail to be sent
            if val["date"] in last_run_set:
                logging.info(
                    f"--trying backlog mail dated={val['date']} for name={val['name']}"
                )
                if not (self.message_func(val, True)):
                    logging.info(
                        f"Backlog email for date {val['date']} and name {val['name']} has failed"
                    )
                    return False
                try:
                    self.send_telegram(val["mobile"], val["name"])
                except Exception as e:
                    logging.error("telegram messaged failed due to %s ", repr(e))
                logging.info(
                    f"Backlog email for date {val['date']} and name {val['name']} has been sent"
                )
                DesktopNotification(
                    "Happy Birthday",
                    f"Backlog email and telegram message for {val['name']} has been sent",
                )

        for i in last_run_with_year_set:
            self.dates_done.append(i)
            modified_dates_file = True

        if modified_dates_file:
            self.sort_date_dones_files()
            save_json_file(self.dates_done_path, self.dates_done)
        return True

    def load_dates_done(self):
        with open(self.dates_done_path, encoding="utf-8") as file:
            self.dates_done = json.load(file)

    def load_birthday_data(self):
        with open(self.data_path, encoding="utf-8") as file:
            self.bday = json.load(file)

    def update_dates_done(self, current_date_withYear):
        self.dates_done.append(current_date_withYear)
        self.sort_date_dones_files()
        save_json_file(self.dates_done_path, self.dates_done)
    @timeit
    def send_mail_from_json(self) -> bool :
        self.load_dates_done()
        current_date_time, current_date_withYear = self.get_current_date()

        if current_date_withYear in self.dates_done:
            logging.info(f"script for {current_date_withYear} has already been executed")
            return None

        if self.download():
            self.load_dates_done()
            if current_date_withYear in self.dates_done:
                logging.info(f"script for {current_date_withYear} has already been executed")
                return None

        current_time = current_date_time.strftime(self.format_string)
        self.download_read_csv_from_server_then_upload()
        self.load_birthday_data()

        if not self.check_for_pending_and_send_message():
            logging.info("---Sending Backlog email failed---")
            return None

        match = False
        for val in self.bday:
            if current_time == val["date"] and self.message_func(val):
                self.send_telegram(val["mobile"], val["name"])
                logging.info(f"email for date {val['date']} and email {val['mail']} has been sent")
                DesktopNotification("Happy Birthday", f"email for {val['name']} has been sent")
                match = True

        if match:
            self.update_dates_done(current_date_withYear)
        else:
            logging.info("--None has birthday today--")
            self.update_dates_done(current_date_withYear)

        return True

    def get_current_date(self) -> Tuple[datetime, str]:
        current_date_time = datetime.now()
        current_date_withyear = current_date_time.strftime(self.format_string_with_year)

        return current_date_time, current_date_withyear

    def sort_date_dones_files(self) -> None:
        # remove duplicates
        self.dates_done = list(set(self.dates_done))
        self.dates_done.sort(
            key=lambda x: datetime.strptime(x, self.format_string_with_year)
        )

    def get_all_birthday_info(self, print_num: str = "a"):
        self.bday: list[dict[str:str]] = json.load(
            open(self.data_path, encoding="utf-8")
        )
        lis = []
        for val in self.bday:
            next_birthday, diff_datetime = self.count_down_for_birthday(val["date"])

            parse_date_to_look_good = datetime.strftime(next_birthday, "%d %b %Y")
            days_rem_mes = f"{diff_datetime.days} days {convert(diff_datetime.seconds)}"

            lis.append(
                [diff_datetime.days, val["name"], parse_date_to_look_good, days_rem_mes]
            )
        lis.sort()
        if print_num != "a":
            lis = lis[: int(print_num)]

        for _, i, j, k in lis:
            print(i, j, k, end="\n\n", sep="\n")

    def count_down_for_birthday(
            self, birthday_string: str
    ) -> tuple[datetime, timedelta]:
        today = datetime.now()
        birthday_string = f"{birthday_string}-{str(next_birth_year(birthday_string))}"
        birthday_ = datetime.strptime(birthday_string, self.format_string_with_year)
        return birthday_, birthday_ - today

    @timeit
    @lru_cache(maxsize=2, typed=False)
    @retry(retries=3, delay=1)
    def download(self):
        return GDrive(FOLDER_NAME, logging).download(self.dates_done_path)

    @timeit
    @retry(retries=3, delay=1)
    def upload(self):
        return GDrive(FOLDER_NAME, logging).upload(self.dates_done_path)

    @timeit
    @lru_cache(maxsize=2, typed=False)
    @retry(retries=3, delay=1)
    def download_read_csv_from_server_then_upload(self):
        GDrive(FOLDER_NAME, logging).download(self.data_path)
        if not csv_to_json():
            logging.info("data has not been changed so not uploading to gdrive")
            return None

        GDrive(FOLDER_NAME, logging).upload(self.data_path)

    @timeit
    @timeout(10)
    @deprecated
    def check_if_session_connection(self) -> Literal[True]:
        return True

    @timeit
    @timeout(timeout_value)
    def send_telegram(self, chat_id, name):
        try:
            with Telegram().client:
                Telegram().message(chat_id, name)
            self.logging.info(f"telegram messages sent to {name}")
        except customTimeOutError:
            logging.error(
                f"sending message to {name} failed due to authentication timeout"
            )
            DesktopNotification(
                title="Telegram authentication failed",message="please re-login"
            )



@timeit
def main():
    birthday = BirthdayMail()
    birthday.check_if_session_connection()

    if birthday.send_mail_from_json() is None:
        logging.info("exiting")
        sys.exit(0)
    # birthday.send_email_special_occassions()
    birthday.upload()
    logging.debug("----Ending the application----")

if __name__ == "__main__":
    import cProfile

    print(os.environ)
    cProfile.run(statement="main()", sort="cumtime", filename="profile.out")
    import pstats

    p = pstats.Stats("profile.out")
    p.sort_stats("cumtime").reverse_order().print_stats()
