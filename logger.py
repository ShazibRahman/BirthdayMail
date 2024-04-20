import logging as log
import pathlib
import sys
from logging.handlers import TimedRotatingFileHandler

from Utils.DesktopNotification import DesktopNotification

logger_path = pathlib.Path(__file__).parent.joinpath("data", "logger.log").resolve()

# Create the logger
logger = log.getLogger()
logger.setLevel(log.INFO)

# Define a TimedRotatingFileHandler to rotate logs daily and keep only the last 5 days' logs
handler = TimedRotatingFileHandler(
    filename=logger_path,
    when='D',          # Rotate daily
    interval=1,        # Interval in days
    backupCount=5      # Keep logs for the last 5 days
)

# Define the log format
formatter = log.Formatter(
    "%(levelname)s - (%(asctime)s): %(message)s (Line: %(lineno)d [%(filename)s])"
)
formatter.datefmt = "%m/%d/%Y %I:%M:%S %p"

# Set the formatter for the file handler
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)

# Add a stream handler to output logs to stdout
stream_handler = log.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

# Define the function to log uncaught exceptions
def log_uncaught_exceptions(exctype, value, traceback):
    if exctype == KeyboardInterrupt:
        return
    logger.exception("Uncaught exception", exc_info=(exctype, value, traceback))
    DesktopNotification("Error", f"{exctype} : {value}")

# Set the exception hook
sys.excepthook = log_uncaught_exceptions

# Export the logger function
def getLogger() -> log.Logger:
    return logger
