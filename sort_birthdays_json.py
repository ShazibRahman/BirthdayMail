import json
from typing import List


def sortBirthdaysObjectOnKey(birthdays: List[object], key: str) -> list:
    """
    sort birthdays object on key (date)
    """
    return sorted(
        birthdays, key=lambda x: x[key].split("-")[1] + "-" + x[key].split("-")[0]
    )


def readJsonFile(fileName: str) -> List[object]:
    with open(fileName, "r") as f:
        return json.load(f)


def writeJsonFile(fileName: str, data: list, indent: int = None) -> None:
    with open(fileName, "w") as f:
        json.dump(data, f, indent=indent)


def main() -> None:
    birthdays = readJsonFile("data.json")
    birthdays = sortBirthdaysObjectOnKey(birthdays, "date")
    writeJsonFile("data.json", birthdays, indent=4)


if __name__ == "__main__":
    main()
