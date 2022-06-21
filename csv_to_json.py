from array import typecodes
import json
import csv
from opcode import opname
from unicodedata import name

def csv_json(csv_path , json_path):
    data :list = json.load(open("/home/shazib/Desktop/Folder/python/BirthdayMessage/data_bk.json"))
    # print(type(data))
    length = len(data)
    names = get_email(data)
    with open(csv_path, encoding='utf-8') as csvf:
        csvReader = csv.DictReader(csvf)
        for rows in csvReader:
            if(rows['mail'] in names):
                print(rows['mail'] , "already in the list ")
            else :
                info ={}
                info['mail'] =rows['mail']
                info['name'] = rows['name']
                date_data = rows['date'].split("-")
                info['date'] = date_data[1]+"-"+date_data[0]
                data.append(info)
        with open(json_path, 'w', encoding='utf-8') as jsonf:
            jsonf.write(json.dumps(data, indent=4))



def get_email(data):
    nmes =set()
    for i in data:
        nmes.add(i['mail'])
    return nmes




if __name__=="__main__":
    csv_json("/home/shazib/Desktop/Folder/python/BirthdayMessage/Little Info.csv", "/home/shazib/Desktop/Folder/python/BirthdayMessage/data.json")
    


