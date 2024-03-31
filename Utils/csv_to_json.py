import csv
import json
import os
import pathlib
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from logger import getLogger  # autopep8: off  # noqa: E402

EMAIL_ADDRESS = "Email Address"
DATE = "date"
MAIL = "mail"
NAME = "name"
MOBILE_NUMBER = "mobile number"
FOLDER_NAME = "BirthDayMail"
MOBILE = "mobile"
log = getLogger()
if __name__ == "__main__":
    from sort_birthdays_json import main as sort_json
else:
    from Utils.sort_birthdays_json import main as sort_json

from gdrive.GDrive import GDrive


def csv_json(csv_path: str, json_path: str) -> None:
    data: list = json.load(open(json_path))
    names = get_email(data)
    with open(csv_path, encoding="utf-8") as csvFile:
        csv_reader = csv.DictReader(csvFile)
        for rows in csv_reader:
            if rows[EMAIL_ADDRESS] in names:
                print(rows[EMAIL_ADDRESS], "already in the list")
            else:
                info = {MAIL: rows[EMAIL_ADDRESS], NAME: rows[NAME]}
                date_data = rows["birth date"].split("/")
                month, day = date_data[0], date_data[1]
                if len(month) == 1:
                    month = f"0{month}"
                if len(day) == 1:
                    day = f"0{day}"
                info[DATE] = f"{day}-{month}"
                info[MOBILE] = (
                    rows[f"+91{MOBILE_NUMBER}"] if rows[MOBILE_NUMBER] != "" else ""
                )
                data.append(info)
                print(rows[EMAIL_ADDRESS], "added to the list")
    os.remove(csv_path)
    sort_json(data)


def get_email(data: list[dict]) -> set[str]:
    return {i[MAIL] for i in data}


def main():
    gdrive = GDrive(FOLDER_NAME, log)
    mimetype = "text/csv"
    file_id = "1IGVrFmTQq-lePEaKWQxEzIAmYy8UwyXgQU0xqyQ3hzc"
    file_path = (
        pathlib.Path(__file__).parent.joinpath("Little Info (Responses).csv").resolve()
    )
    gdrive.download_by_id_and_file_format(file_path, file_id, mimetype)

    csv_json(
        file_path,
        pathlib.Path(__file__).parent.parent.joinpath("data", "data.json").resolve(),
    )


if __name__ == "__main__":
    data_file = (
        pathlib.Path(__file__).parent.parent.joinpath("data", "data.json").resolve()
    )
    gdrive = GDrive(FOLDER_NAME, log)
    mimetype = "text/csv"
    gdrive.download(data_file)
    file_id = "1IGVrFmTQq-lePEaKWQxEzIAmYy8UwyXgQU0xqyQ3hzc"
    file_path = (
        pathlib.Path(__file__).parent.joinpath("Little Info (Responses).csv").resolve()
    )
    gdrive.download_by_id_and_file_format(file_path, file_id, mimetype)

    csv_json(file_path, data_file)
    gdrive.upload(data_file)
