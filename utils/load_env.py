import logging
import os
import pathlib


logger = logging.getLogger()


class load_env:

    """
    A simple load_env class who main job is to load_ebv to the system ..
    It reads fom .systemenv file
    Not using .env file for security and flexibility reasons
    """

    def __init__(self):
        self.env_file = (
            pathlib.Path(__file__).parent.parent.joinpath(".Systemenv").resolve()
        )
        self.on_load()

    def on_load(self):
        with open(self.env_file, "r") as env_file:
            for line in env_file:
                if line.strip() == "":
                    continue
                key, value = line.strip().split(":=")
                key, value = key.strip(), value.strip()
                os.environ[key] = value


if __name__ == "__main__":
    load_env()

    print(type(os.getenv("TIMEOUTVALUE")))
    print(os.getenv("TIMEOUTVALUE"))
