
import logging
import os
import pathlib

from .time_it import timeit

logger = logging.getLogger()

class load_env:

    def __init__(self):
        self.env_file = pathlib.Path(__file__).parent.parent.joinpath(
            ".Systemenv").resolve()
        self.on_load()
        logger.info("load_env")
    
    @timeit
    def on_load(self):
        with open(self.env_file, 'r') as env_file:
            for line in env_file:
                if line.strip() == "":
                    continue
                key, value = line.strip().split(":=")
                key, value = key.strip(), value.strip()
                os.environ[key] = value


if __name__ == "__main__":
    load_env()

    print(type(os.getenv("TIMEOUTVALUE")))
