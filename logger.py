import logging as log
import pathlib
import sys

from utils.DesktopNotification import DesktopNotification

logger_path = pathlib.Path(__file__).parent.joinpath("data", "logger.log").resolve()

if not pathlib.Path.exists(logger_path):
    open(logger_path, "w", encoding="utf-8").close()

formatter = log.Formatter(
    "%(levelname)s - (%(asctime)s): %(message)s (Line: %(lineno)d [%(filename)s])"
)
formatter.datefmt = "%m/%d/%Y %I:%M:%S %p"

log.basicConfig(
    filename=logger_path,
    filemode="a",
    level=log.INFO,
    format="%(levelname)s - (%(asctime)s): %(message)s (Line: %(lineno)d [%(filename)s])",
    datefmt="%m/%d/%Y %I:%M:%S %p",
)
stream_handler = log.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)

log.getLogger().addHandler(stream_handler)


def log_uncaught_exceptions(exctype, value, traceback):
    log.exception("Uncaught exception", exc_info=(exctype, value, traceback))
    DesktopNotification("Error", f"{exctype} : {value}")


sys.excepthook = log_uncaught_exceptions


def getLogger() -> log.Logger:
    return log
