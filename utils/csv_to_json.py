import json
import csv
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from sort_birthdays_json import main
from gdrive.GDrive import GDrive

def csv_json(csv_path: str, json_path: str) -> None:
    data: list = json.load(
        open(json_path)
    )
    names = get_email(data)
    with open(csv_path, encoding="utf-8") as csvFile:
        csvReader = csv.DictReader(csvFile)
        for rows in csvReader:
            if rows["Email Address"] in names:
                print(rows["Email Address"], "already in the list")
            else:
                info = {"mail": rows["Email Address"], "name": rows["name"]}
                date_data = rows["birth date"].split("/")
                month,day = date_data[0], date_data[1]
                if len(month) == 1:
                    month = "0" + month
                if len(day) == 1:
                    day = "0" + day
                info["date"] = day + "-" + month
                data.append(info)
                print(rows["Email Address"], "added to the list")
    main(data)


def get_email(data) -> set:
    names = set()
    for i in data:
        names.add(i["mail"])
    return names


if __name__ == "__main__":
    gdrive =  GDrive()
    mimetype  = "text/csv"
    file_id = "1IGVrFmTQq-lePEaKWQxEzIAmYy8UwyXgQU0xqyQ3hzc"
    file_path = os.path.join(os.path.dirname(__file__), "Little Info (Responses).csv")
    gdrive.download_by_id_and_file_format(file_path, file_id, mimetype)
 

    csv_json(
        file_path,
        os.path.join(os.path.dirname(__file__),"..", "data.json")
    )

