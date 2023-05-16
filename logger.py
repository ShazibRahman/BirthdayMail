import logging as log
import pathlib
import sys

logger_path = pathlib.Path(__file__).parent.joinpath(
    "data", "logger.log").resolve()

if not pathlib.Path.exists(logger_path):
    open(logger_path, "w").close()

log.basicConfig(
    filename=logger_path,
    filemode="a",
    level=log.INFO,
    format="%(asctime)s %(message)s         %(filename)s  %(lineno)d",
    datefmt="%m/%d/%Y %I:%M:%S %p",
)
log.getLogger().addHandler(log.StreamHandler(sys.stdout))

def getLogger() -> log.Logger:
    return log
