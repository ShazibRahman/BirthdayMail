import json


def sortBirthdaysObjectOnKey(birthdays, key):
    return sorted(
        birthdays,
        key=lambda x: x[key].split("-")[1] + "-" + x[key].split("-")[0])


def readJsonFile(fileName):
    with open(fileName, "r") as f:
        return json.load(f)


def writeJsonFile(fileName, data, indent=None):
    with open(fileName, "w") as f:
        json.dump(data, f, indent=indent)


def main():
    birthdays = readJsonFile("data.json")
    birthdays = sortBirthdaysObjectOnKey(birthdays, "date")
    writeJsonFile("data.json", birthdays, indent=4)


if __name__ == "__main__":
    main()