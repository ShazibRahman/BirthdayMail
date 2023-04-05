import json
import os


def sortBirthdaysObjectOnKey(birthdays: list, key: str) -> list:
    """
    sort birthdays object on key (date)
    """
    return sorted(
        birthdays, key=lambda x: x[key].split(
            "-")[1] + "-" + x[key].split("-")[0]
    )


def readJsonFile(fileName: str) -> list:
    with open(fileName, "r") as f:
        return json.load(f)


def writeJsonFile(fileName: str, data: list, indent: int = 4) -> None:
    with open(fileName, "w") as f:
        json.dump(data, f, indent=indent)


def main() -> None:
    dir = os.path.dirname(__file__)
    data_path = os.path.join(dir, 'data.json')
    birthdays = readJsonFile(data_path)
    birthdays = sortBirthdaysObjectOnKey(birthdays, "date")
    writeJsonFile(data_path, birthdays)


if __name__ == "__main__":
    main()
