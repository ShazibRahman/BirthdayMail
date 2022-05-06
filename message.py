#!/home/shazib/Desktop/linux/test/bin/python
from asyncio.log import logger
import json
import smtplib, ssl
from email.message import EmailMessage
import os
from datetime import datetime
import logging
import time
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
    return time.strftime("%H hours %M Minutes %S Seconds to go " , time.gmtime(seconds))
      

def render_template(template, context):
    return template.render(context)


class BirthdayMail:

    def __init__(self) -> None:
        logging.info(f"current working directory {os.getcwd()}")
        logging.info("----Starting the application-----")
        self.directoryString = os.path.dirname(__file__)
        self.sender_email = os.environ.get('shazmail')
        self.password = os.environ.get('shazPassword')
        self.template_filename = self.directoryString + "/html_template.html"
        self.template_to_render = Template(open(self.template_filename).read())
        self.formatString = "%d-%m"
        self.bday = json.load(open(self.directoryString + "/data.json"))

    def message_func(self, receiver_email, name:str):
        message = EmailMessage()
        message["Subject"] = "Happy Birthday "+name.split("(")[0]
        message["From"] = self.sender_email
        message["To"] = receiver_email
        context_template = render_template(self.template_to_render,
                                           {"name": name})
        message.set_content(context_template, subtype="html")
        context = ssl.create_default_context()
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
    def get_all_bday_info(self):
        logging.info("getting all the bday data")
        for val in self.bday:
            date_info_today= datetime.now()
            cur_year = date_info_today.year
            datetime_format = datetime.strptime(val['date']+"-"+str(cur_year),self.formatString+"-%Y")
            if date_info_today > datetime_format:
                datetime_format = datetime.strptime(val['date']+"-"+str(cur_year+1),self.formatString+"-%Y")

            parse_date_to_look_good =datetime.strftime(datetime_format ,"%d %b %Y")
            diff_datetime = datetime_format-date_info_today
            days_rem_mes =  f"{diff_datetime.days} days {convert(diff_datetime.seconds)}"
            

            print(val['name'] , parse_date_to_look_good ,days_rem_mes ,end="\n\n", sep="\n")




if __name__ == "__main__":
    birthday = BirthdayMail()
    birthday.send_mail_from_json()
    # birthday.get_all_bday_info()
