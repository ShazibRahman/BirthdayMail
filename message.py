#!/home/shazib/Desktop/linux/test/bin/python
import json
import smtplib
import ssl
from email.message import EmailMessage
import os
from datetime import  datetime
import logging
import time
from typing import Tuple


try:
    from jinja2 import Template
except:
    print('please run this command `pip install jinja2`')

logging.basicConfig(filename=os.path.dirname(__file__) + '/logger.log',
                    filemode='a',
                    level=logging.DEBUG,
                    format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')


def convert(seconds):
    return time.strftime("%H hours %M Minutes %S Seconds to go ",
                         time.gmtime(seconds))


def render_template(template, context):
    return template.render(context)


class BirthdayMail:

    def __init__(self) -> None:
        if os.environ.get('USER') == "Shazib_Anacron":
            logging.info(f"logged in as {os.environ.get('USER')}")
            logging.info("----Starting the application-----")
        self.directoryString = os.path.dirname(__file__)
        self.sender_email = os.environ.get('shazmail')
        self.password = os.environ.get('shazPassword')
        self.template_filename = self.directoryString + "/html_template.html"
        self.template_to_render = Template(open(self.template_filename).read())
        self.formatString = "%d-%m"
        self.formatStringWithYear = "%d-%m-%Y"
        self.bday = json.load(open(self.directoryString + "/data.json"))

    def message_func(self, receiver_email:str, name: str):
        message = EmailMessage()
        message["Subject"] = "Happy Birthday " + name.split("(")[0]
        message["From"] = self.sender_email
        message["To"] = receiver_email
        context_template = render_template(self.template_to_render,
                                           {"name": name})
        message.set_content(context_template, subtype="html")
        with smtplib.SMTP_SSL("smtp.gmail.com",
                              465,
                              context=ssl.create_default_context()) as server:
            server.login(self.sender_email, self.password)
            server.send_message(message)
            logging.info(
                f"The email has been sent to {name} with email {receiver_email}"
            )

    def send_mail_from_json(self):
        current_time = datetime.strftime(datetime.now(), self.formatString)
        match = False
        for val in self.bday:
            if current_time == val['date']:
                self.message_func(val['mail'], val['name'])
                match = True
        if not match:
            logging.info("--None has birthday today--")

    def get_all_bday_info(self, print_all: bool = False):
        # logging.info("getting all the bday data")
        lis = []
        for val in self.bday:
            next_birthday, diff_datetime = self.count_down_for_birthday(
                val['date'])

            parse_date_to_look_good = datetime.strftime(
                next_birthday, "%d %b %Y")
            days_rem_mes = f"{diff_datetime.days} days {convert(diff_datetime.seconds)}"

            # print(val['name'] , parse_date_to_look_good ,days_rem_mes ,end="\n\n", sep="\n")
            lis.append([
                diff_datetime.days, val['name'], parse_date_to_look_good,
                days_rem_mes
            ])  # saving it in key value pair where key is the rem day for bd
        lis.sort()
        if not print_all:
            lis = lis[:3]

        for l, i, j, k in lis:
            print(i, j, k, end="\n\n", sep="\n")

    def isGreater(self, day1:int, month1:int, day2:int, month2:int)->bool:
        if month1 > month2:
            return True
        elif month1 == month2 and day1 > day2:
            return True
        else:
            return False

    def isLeapYear(self, year: int) -> bool:
        if year % 4 == 0 and year % 100 != 0 or year % 400 == 0:
            return True
        else:
            return False

    def nextBirthYear(self, birthdayString: str) -> int:
        day1, month1 = birthdayString.split("-")
        today = datetime.now()
        day2, month2, year = today.day, today.month, today.year
        if month1 == "02" and day1 == "29":
            if self.isGreater(int(day1), int(month1), day2,
                              month2) and self.isLeapYear(year):
                return year
            else:
                return self.find_next_leap_year(year)

        elif self.isGreater(int(day1), int(month1), day2, month2):
            return year
        else:
            return year + 1

    def find_next_leap_year(self, year: int) -> int:
        if year % 4 == 0 and year % 100 != 0 or year % 400 == 0:
            return year + 4
        elif year % 4 != 0:
            return year + year % 4
        elif year % 4 == 0 and year % 100 == 0 or year % 400 != 0:
            return year + 4
        else:
            return year

    def count_down_for_birthday(
            self, birthdayString: str) -> Tuple[datetime, datetime]:
        today = datetime.now()
        birthdayString = birthdayString + "-" + str(
            self.nextBirthYear(birthdayString))
        birthday = datetime.strptime(birthdayString, self.formatStringWithYear)
        return birthday, birthday - today


if __name__ == "__main__":
    birthday = BirthdayMail()
    birthday.send_mail_from_json()
    # birthday.get_all_bday_info()
