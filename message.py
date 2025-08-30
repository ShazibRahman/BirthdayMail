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
from typing import Tuple

from gdrive.GDrive import GDrive

from decorator_utils import timeit
from decorator_utils import timeout,customTimeOutError
from decorator_utils import lock_manager_decorator
from decorator_utils import connectivity,check_connection_decorator
from decorator_utils import retry


# from Decorators.time_it import timeit
from Utils.DesktopNotification import DesktopNotification
from Utils.csv_to_json import main as csv_to_json
from telegram.telegram import Telegram
from data.images import image_list  # type: ignore
import logger  # type: ignore



pwd = pathlib.Path(__file__).parent.resolve()

try:
    from jinja2 import Template

except ImportError:
    if os.name == "nt":
        os.system("pip install -r requirement.txt")
    else:
        os.system("pip3 install -r requirement.txt")
    from jinja2 import Template


FOLDER_NAME = "BirthDayMail"
timeout_value = int(os.getenv("TIMEOUTVALUE", "10"))

HOST = "smtp.gmail.com"
PORT = 465


def convert(seconds: int) -> str:
    """
    Converts a given number of seconds into a formatted string
    representing hours, minutes, and seconds.

    Args:
        seconds (int): The number of seconds to convert.

    Returns:
        str: A string representing the time in the format
            "H hours M Minutes S Seconds to go".
    """

    return time.strftime("%H hours %M Minutes %S Seconds to go ", time.gmtime(seconds))


def render_template(template: Template, context: dict) -> str:
    """
    Renders a template with the provided context, adding a random image.

    This function selects a random image from the `image_list` and adds it
    to the context under the "image" key. It then renders the given Jinja2
    template using this updated context.

    Args:
        template (Template): The Jinja2 template object to be rendered.
        context (dict): A dictionary containing the variables to be used
            during rendering.

    Returns:
        str: The rendered template as a string.
    """

    context["image"] = random.choice(image_list)

    return template.render(context)


@timeit
def save_json_file(file_name: str, data: list, indent: int = 4) -> None:
    """
    Saves the given data to a JSON file.

    Args:
        file_name (str): The name of the file to save the data to.
        data (list): The data to be saved.
        indent (int): The indentation level for the JSON file. Defaults to 4.

    Returns:
        None
    """
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent)
    logging.info(f"write changes to {file_name=}")


@timeit
def read_json_to_py_object(file_name: str):
    """
    Reads a JSON file and converts it into a Python object.

    Args:
        file_name (str): The path to the JSON file.

    Returns:
        A Python object that is the result of decoding the JSON file.
    """
    with open(file_name, encoding="utf-8") as f:
        return json.load(f)


def find_next_leap_year(year: int) -> int:
    """
    This function takes an integer year as argument and returns the next leap year.

    The algorithm works as follows:
    - If the year is already a leap year, it adds 4 to it.
    - If the year is not a leap year and the remainder of the year divided by 4 is not 0,
      it adds the remainder to the year.
    - In all other cases, it adds 4 to the year.
    """
    if year % 4 == 0 and year % 100 != 0 or year % 400 == 0:
        return year + 4
    elif year % 4 != 0:
        return year + year % 4
    else:
        return year + 4


def is_leap_year(year: int) -> bool:
    """
    Checks if a given year is a leap year.

    A leap year is exactly divisible by 4 except for century years (years ending with 00).
    The century year is a leap year only if it is perfectly divisible by 400.
    This means that in the Gregorian calendar, the years 2000 and 2400 are leap years,
    while 1800, 1900, 2100, 2200, 2300 and 2500 are not.

    Args:
        year (int): The year to check

    Returns:
        bool: True if the year is a leap year, False otherwise
    """
    return year % 4 == 0 and year % 100 != 0 or year % 400 == 0


def is_greater(day1: int, month1: int, day2: int, month2: int) -> bool:
    """
    Determines if the date represented by (day1, month1) is later than
    the date represented by (day2, month2).

    Args:
        day1 (int): The day of the first date.
        month1 (int): The month of the first date.
        day2 (int): The day of the second date.
        month2 (int): The month of the second date.

    Returns:
        bool: True if the first date is later than the second date, False otherwise.
    """

    return month1 > month2 or month1 == month2 and day1 > day2


@timeit
def send_mail(sender_email: str, password: str, message: EmailMessage) -> bool:
    """
    Send an email using smtplib.

    :param sender_email: The sender's email address
    :param password: The sender's email password
    :param message: The EmailMessage object to send
    :return: True if the email was sent successfully, False otherwise
    """
    ctx: ssl.SSLContext = ssl.create_default_context()
    ctx.verify_mode = ssl.CERT_REQUIRED
    try:
        with smtplib.SMTP_SSL(HOST, PORT, context=ctx) as server:
            server.login(sender_email, password)
            server.send_message(message)
            logging.info(f"---Mail sent to {message['To']}---")
    except Exception as e:
        logging.error(f"---Network Error---{repr(e)}")
        return False
    return True


def next_birth_year(birthday_string: str) -> int:
    """
    Calculates the year of the next birthday of a person given their birthday string "DD-MM".
    If the birthday is 29th February, it will return the next leap year if the current year is not a leap year.
    If the birthday has already passed this year, it will return the next year.
    :param birthday_string: A string in the format "DD-MM" representing the birthday
    :return: The year of the next birthday of the person
    """
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

# lock_manager = LockManager(lock_file)


class BirthdayMail:
    def __init__(self) -> None:
        """
        Initializes the class and sets up the necessary instance variables.

        :param None

        :return None
        """

        # if not lock_manager.acquire_control():
        #     sys.exit(1)

        self.bday = None
        self.dates_done = None
        logging.info("----Starting the application----")
        self.logging = logging

        self.template_filename = None
        self.template_to_render = None
        self.directory_string = os.path.dirname(__file__)
        self.sender_email: str = os.environ.get("shazmail")  # type: ignore
        self.password: str = os.environ.get("shazPassword")  # type: ignore
        if user := os.environ.get("USER"):
            logging.info(f"--logged in as {user=}")

        self.format_string = "%d-%m"
        self.format_string_with_year = "%d-%m-%Y"
        self.format_late_mail_date = "%d-%b"

        self.data_path = pathlib.Path(self.directory_string).joinpath(
            "data", "data.json"
        )
        self.dates_done_path = pathlib.Path(self.directory_string).joinpath(
            "data", "dates.json"
        )

    def __del__(self):
        """
        Releases the lock.
        """
        # lock_manager.release_control()

    def message_func(self, val: dict, pending_mail=False) -> bool:
        """
        Function to send birthday email.

        Args:
            val (dict): A dictionary containing email address and name of the birthday person.
            pending_mail (bool, optional): Whether this is a pending mail or not. Defaults to False.

        Returns:
            bool: True if the email was sent successfully, False otherwise.
        """
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
        """
        This function is responsible for sending pending birthday emails.

        It checks if today's date is the same as the last date stored in the dates_done file.
        If it is the same, then it returns True as there are no pending emails to be sent.
        If it is not the same, it calculates the difference and for each of the dates in the difference,
        it checks if there is any birthday mail to be sent. If there is, it sends the email and telegram message.

        Finally, it updates the dates_done file with the current date.

        Returns:
            bool: True if all the pending emails were sent successfully, False otherwise.
        """
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
                if not self.message_func(val, True):
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
        """
        Loads the dates_done data from a JSON file and assigns it to the instance variable.

        The JSON file is located at the path specified by the dates_done_path attribute.
        It is expected to contain a list of dates representing the dates for which
        birthday emails have already been sent.

        Raises:
            JSONDecodeError: If the file contains invalid JSON.
            FileNotFoundError: If the file does not exist.
        """

        with open(self.dates_done_path, encoding="utf-8") as file:
            self.dates_done = json.load(file)

    def load_birthday_data(self):
        """
        Loads birthday data from a JSON file and assigns it to the instance variable.

        The JSON file is located at the path specified by the data_path attribute.
        It is expected to contain a list of dictionaries, each representing an individual's birthday information.

        Raises:
            JSONDecodeError: If the file contains invalid JSON.
            FileNotFoundError: If the file does not exist.
        """
        with open(self.data_path, encoding="utf-8") as file:
            self.bday = json.load(file)

    def update_dates_done(self, current_date_with_year):
        """
        Updates the dates_done list with the given current date.

        Args:
            current_date_withYear (str): The current date in the format "DD-MM-YYYY".

        Returns:
            None
        """
        self.dates_done.append(current_date_with_year)
        self.sort_date_dones_files()
        self.dates_done = self.dates_done[-20:]
        save_json_file(self.dates_done_path, self.dates_done)

    @timeit
    @lock_manager_decorator(lock_file)
    def send_mail_from_json(self) -> bool:
        """
        Sends birthday emails and updates records from JSON data.

        This function checks if the email script for the current date
        has already been executed. If not, it downloads necessary data,
        processes pending birthday emails, and sends notifications via
        email and Telegram. It ensures that no duplicate emails are sent
        for the same date and updates the records once emails are sent.

        Returns:
            bool: True if the emails were sent successfully, None otherwise.
        """

        self.load_dates_done()
        current_date_time, current_date_withYear = self.get_current_date()

        if current_date_withYear in self.dates_done:
            logging.info(
                f"script for {current_date_withYear} has already been executed"
            )
            return None

        if self.download():
            self.load_dates_done()
            if current_date_withYear in self.dates_done:
                logging.info(
                    f"script for {current_date_withYear} has already been executed"
                )
                return None

        current_time = current_date_time.strftime(self.format_string)
        self.upload_data()
        self.load_birthday_data()

        if not self.check_for_pending_and_send_message():
            logging.info("---Sending Backlog email failed---")
            return None

        match = False
        for val in self.bday:
            if current_time == val["date"] and self.message_func(val):
                try:
                    self.send_telegram(val["mobile"], val["name"])
                except Exception as e:
                    logging.error("telegram messaged failed due to %s ", repr(e))
                logging.info(
                    f"email for date {val['date']} and email {val['mail']} has been sent"
                )
                DesktopNotification(
                    "Happy Birthday", f"email for {val['name']} has been sent"
                )
                match = True

        if not match:
            logging.info("--None has birthday today--")
        self.update_dates_done(current_date_withYear)
        return True

    def get_current_date(self) -> Tuple[datetime, str]:
        """
        Return the current date as a tuple of a datetime object and a string
        in the format defined in self.format_string_with_year.

        Returns:
            Tuple[datetime, str]: A tuple containing the current datetime object
            and the current date in the format defined in self.format_string_with_year.
        """
        current_date_time = datetime.now()
        current_date_withyear = current_date_time.strftime(self.format_string_with_year)

        return current_date_time, current_date_withyear

    def sort_date_dones_files(self) -> None:
        """
        Sorts and removes duplicates from the dates_done list.

        The function converts the dates_done list into a set to remove duplicate entries,
        and then sorts the list in chronological order based on the date format defined
        in self.format_string_with_year.

        Returns:
            None
        """

        self.dates_done = list(set(self.dates_done))
        self.dates_done.sort(
            key=lambda x: datetime.strptime(x, self.format_string_with_year)
        )

    def get_all_birthday_info(self, print_num: str = "a"):
        """
        Prints the next birthday information for all the contacts in the database.

        Args:
            print_num (str, optional): The number of contacts to print the birthday information for.
                If 'a', prints information for all contacts. Defaults to 'a'.

        Raises:
            ValueError: If `print_num` is not a digit or 'a'.

        """
        with open(self.data_path, encoding="utf-8") as file:
            self.bday: list[dict[str:str]] = json.load(file)

        lis = []
        for val in self.bday:
            next_birthday, diff_datetime = self.count_down_for_birthday(val["date"])
            parse_date_to_look_good = datetime.strftime(next_birthday, "%d %b %Y")
            days_rem_mes = f"{diff_datetime.days} days {convert(diff_datetime.seconds)}"
            lis.append(
                {
                    "name": val["name"],
                    "next_birthday": parse_date_to_look_good,
                    "remaining_days": days_rem_mes,
                    "days": diff_datetime.days,
                }
            )

        lis.sort(key=lambda x: x["days"])

        if print_num.isdigit():
            lis = lis[: int(print_num)]
        elif print_num.strip().lower() != "a":
            raise ValueError(
                "Invalid input for print_num. Expected a digit or 'a', got: "
                + print_num
            )

        for info in lis:
            print(
                info["name"],
                info["next_birthday"],
                info["remaining_days"],
                sep="\n",
                end="\n\n",
            )

    def count_down_for_birthday(
        self, birthday_string: str
    ) -> tuple[datetime, timedelta]:
        """
        Calculates the next birthday datetime and timedelta from today's date.

        :param birthday_string: A string in the format "DD-MM" representing the birthday
        :return: A tuple containing the next birthday datetime and timedelta from today's date
        """
        today = datetime.now()
        birthday_string = f"{birthday_string}-{str(next_birth_year(birthday_string))}"
        birthday_ = datetime.strptime(birthday_string, self.format_string_with_year)
        return birthday_, birthday_ - today

    @timeit
    @lru_cache(maxsize=2, typed=False)
    @retry(retries=3, delay=1)
    @timeout(15)
    def download(self):
        """
        Downloads the dates_done file from Google Drive using the GDrive class.

        This function is decorated with @timeit to measure the time it takes to execute,
        @lru_cache(maxsize=2, typed=False) to cache the result of the function for 2
        different arguments, @retry(retries=3, delay=1) to retry the function 3 times
        with a delay of 1 second between retries if it fails, and @timeout(15) to timeout
        the function after 15 seconds if it takes longer than that to complete.

        Returns:
            bool: True if the file was downloaded successfully, False otherwise.
        """
        return GDrive(FOLDER_NAME).download(self.dates_done_path)

    @timeit
    @retry(retries=3, delay=1)
    def upload(self):
        """
        Uploads the dates_done file to Google Drive using the GDrive class.

        This function is decorated with @timeit to measure the time it takes to execute,
        and @retry(retries=3, delay=1) to retry the function 3 times with a delay of 1 second
        between retries if it fails.

        Returns:
            bool: True if the file was uploaded successfully, False otherwise.
        """
        return GDrive(FOLDER_NAME).upload(self.dates_done_path)

    @timeit
    @lru_cache(maxsize=2, typed=False)
    @retry(retries=3, delay=1)
    @timeout(15)
    def upload_data(self):
        GDrive(FOLDER_NAME).upload(self.data_path)

    @timeit
    @timeout(timeout_value)
    def send_telegram(self, chat_id, name):
        """
        Sends a Telegram message to a specified chat ID.

        This function utilizes the Telegram class to send a message to a specified chat ID and logs
        the result. It is decorated with @timeit to measure execution time and @timeout to enforce
        a timeout on the function execution.

        Args:
            chat_id: The ID of the chat where the message will be sent.
            name: The name to be included in the message.

        Raises:
            customTimeOutError: If the message sending process exceeds the specified timeout.
        """

        try:
            with Telegram().client:
                Telegram().message(chat_id, name)
            self.logging.info(f"telegram messages sent to {name}")
        except customTimeOutError:
            logging.error(
                "sending message to %s failed due to authentication timeout", name
            )
            DesktopNotification(
                title="Telegram authentication failed", message="please re-login"
            )


@timeit
def main():
    """
    Main function of the program.

    Instantiates a BirthdayMail object and calls its send_mail_from_json method to send birthday emails.
    If the method returns None, the program exits.
    Then, the upload method of the BirthdayMail object is called to upload the JSON file to Google Drive.
    Finally, a debug message is logged to mark the end of the application.

    Returns:
        None
    """
    birthday = BirthdayMail()
    if birthday.send_mail_from_json() is None:
        logging.info("exiting")
        sys.exit(0)
    # birthday.send_email_special_occassions()
    birthday.upload()
    logging.debug("----Ending the application----")


if __name__ == "__main__":
    main()
