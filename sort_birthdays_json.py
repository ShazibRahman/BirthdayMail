import json
import os
from rich.console import Console
console = Console()


def sortBirthdaysObjectOnKey(birthdays: list, key: str) -> list:
    """
    sort birthdays object on key (date)
    """
    console.log("Sorting birthdays")
    return sorted(
        birthdays, key=lambda x: x[key].split(
            "-")[1] + "-" + x[key].split("-")[0]
    )


def readJsonFile(fileName: str) -> list:
    console.log(f"Reading {fileName}")
    with open(fileName, "r") as f:
        return json.load(f)


def writeJsonFile(fileName: str, data: list, indent: int = 4) -> None:
    console.log(f"Writing {fileName}")
    with open(fileName, "w") as f:
        json.dump(data, f, indent=indent)


def main(data) -> None:
    dir = os.path.dirname(__file__)
    data_path = os.path.join(dir, "data.json")
    birthdays_sorted = sortBirthdaysObjectOnKey(data, "date")
    if birthdays_sorted == data:
        console.log("Birthdays are already sorted")
        return
    writeJsonFile(data_path, birthdays_sorted)


if __name__ == "__main__":
    main()
