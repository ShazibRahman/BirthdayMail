

import os
import pathlib


class load_env:

    def __init__(self):
        self.env_file = pathlib.Path(__file__).parent.parent.joinpath(
            ".env").resolve()
        self.on_loaad()

    def on_loaad(self):
        with open(self.env_file, 'r') as env_file:
            for line in env_file:
                if line.strip() == "":
                    continue
                key, value = line.strip().split("=")
                key, value = key.strip(), value.strip()
                os.environ[key] = value


if __name__ == "__main__":
    load_env()

    print(type(os.getenv("TIMEOUTVALUE")))
