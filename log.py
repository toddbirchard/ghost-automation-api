"""Custom logger."""
import json
from os import path
from sys import stdout

from loguru import logger

from config import settings


def json_formatter(record: dict) -> str:
    """
    Pass raw log to be serialized.

    :param dict record: Dictionary containing logged message with metadata.

    :returns: str
    """

    def serialize(log: dict) -> str:
        """
        Parse log message into Datadog JSON format.

        :param dict log: Dictionary containing logged message with metadata.

        :returns: str
        """
        subset = {
            "time": log["time"].strftime("%m/%d/%Y, %H:%M:%S"),
            "message": log["message"],
            "level": log["level"].name,
            "function": log.get("function"),
            "module": log.get("name"),
        }
        if log.get("exception", None):
            subset.update({"exception": log["exception"]})
        return json.dumps(subset)

    record["extra"]["serialized"] = serialize(record)
    return "{extra[serialized]},\n"


def log_formatter(record: dict) -> str:
    """
    Formatter for .log records

    :param dict record: Key/value object containing a single log's message & metadata.

    :returns: str
    """
    if record["level"].name == "TRACE":
        return "<fg #5278a3>{time:MM-DD-YYYY HH:mm:ss}</fg #5278a3> | <fg #cfe2f3>{level}</fg #cfe2f3>: <light-white>{message}</light-white>\n"
    if record["level"].name == "INFO":
        return "<fg #5278a3>{time:MM-DD-YYYY HH:mm:ss}</fg #5278a3> | <fg #b3cfe7>{level}</fg #b3cfe7>: <light-white>{message}</light-white>\n"
    if record["level"].name == "WARNING":
        return "<fg #5278a3>{time:MM-DD-YYYY HH:mm:ss}</fg #5278a3> |  <fg #b09057>{level}</fg #b09057>: <light-white>{message}</light-white>\n"
    if record["level"].name == "SUCCESS":
        return "<fg #5278a3>{time:MM-DD-YYYY HH:mm:ss}</fg #5278a3> | <fg #6dac77>{level}</fg #6dac77>: <light-white>{message}</light-white>\n"
    if record["level"].name == "ERROR":
        return "<fg #5278a3>{time:MM-DD-YYYY HH:mm:ss}</fg #5278a3> | <fg #a35252>{level}</fg #a35252>: <light-white>{message}</light-white>\n"
    return "<fg #5278a3>{time:MM-DD-YYYY HH:mm:ss}</fg #5278a3> | <fg #b3cfe7>{level}</fg #b3cfe7>: <light-white>{message}</light-white>\n"


def create_logger() -> logger:
    """
    Configure custom logger.

    :returns: logger
    """
    logger.remove()
    logger.add(
        stdout,
        colorize=True,
        catch=True,
        level="TRACE",
        format=log_formatter,
    )
    if settings.ENVIRONMENT == "production" and path.isdir("/var/log/api"):
        # Datadog JSON logs
        logger.add(
            "/var/log/api/info.json",
            format=json_formatter,
            rotation="200 MB",
            level="TRACE",
            compression="zip",
        )
        # Readable logs
        logger.add(
            "/var/log/api/info.log",
            colorize=True,
            catch=True,
            level="TRACE",
            format=log_formatter,
            rotation="200 MB",
            compression="zip",
        )
    else:
        logger.add(
            f"/logs/error.log",
            colorize=True,
            catch=True,
            format=log_formatter,
            rotation="200 MB",
            compression="zip",
            level="ERROR",
        )
    return logger


# Custom logger
LOGGER = create_logger()
