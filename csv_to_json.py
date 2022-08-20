import json
import csv


def csv_json(csv_path:str, json_path:str)->None:
    data: list = json.load(
        open("/home/shazib/Desktop/Folder/python/BirthdayMessage/data.json"))
    names = get_email(data)
    with open(csv_path, encoding='utf-8') as csvf:
        csvReader = csv.DictReader(csvf)
        for rows in csvReader:
            if (rows['Username'] in names):
                print(rows['Username'], "already in the list ")
            else:
                info = {}
                info['mail'] = rows['Username']
                info['name'] = rows['name']
                date_data = rows['birth date'].split("-")
                info['date'] = date_data[1] + "-" + date_data[0]
                data.append(info)
        with open(json_path, 'w', encoding='utf-8') as jsonf:
            jsonf.write(json.dumps(data, indent=4))


def get_email(data)->set:
    nmes = set()
    for i in data:
        nmes.add(i['mail'])
    return nmes


if __name__ == "__main__":
    csv_json("/home/shazib/Little Info.csv",
             "/home/shazib/Desktop/Folder/python/BirthdayMessage/data.json")
