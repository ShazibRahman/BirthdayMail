import json
import pathlib
from rich.console import Console

console = Console()

data_path = pathlib.Path(__file__).parent.parent.joinpath("data", "data.json")


def sort_birthdays_object_on_key(birthdays: list, key: str) -> list:
    """
    sort birthdays object on key (date)
    """
    console.log("Sorting birthdays")
    return sorted(
        birthdays, key=lambda x: x[key].split("-")[1] + "-" + x[key].split("-")[0]
    )


def read_json_file(file_name: str | pathlib.Path) -> list:
    """

    Args:
        file_name:

    Returns:

    """
    console.log(f"Reading {file_name}")
    with open(file_name, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json_file(file_name: str | pathlib.Path, data: list, indent: int = 4) -> None:
    """

    Args:
        file_name:
        data:
        indent:

    Returns:

    """
    console.log(f"Writing {file_name}")
    with open(file_name, "w") as f:
        json.dump(data, f, indent=indent)


def main(data) -> bool:
    """

    Args:
        data:

    Returns:

    """
    # print(data_path)
    birthdays_sorted = sort_birthdays_object_on_key(data, "date")
    if birthdays_sorted == data:
        console.log("Birthdays are already sorted")
        return False
    write_json_file(data_path, birthdays_sorted)
    return True


if __name__ == "__main__":
    data = read_json_file(data_path)
    main(data)
