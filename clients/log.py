"""Custom logger."""
from sys import stdout, stderr
import simplejson as json
from loguru import logger
from config import Config


def serialize(record):
    """Parse log message into Datadog JSON format."""
    subset = {
        "time": record["time"].strftime("%m/%d/%Y, %H:%M:%S"),
        "message": record["message"],
        "function": record["function"],
        "module": record["name"]
    }
    if record.get("exception", None):
        subset.update({'exception': record["exception"]})
    return json.dumps(subset)


def formatter(record):
    """Pass raw string to be serialized."""
    record["extra"]["serialized"] = serialize(record)
    return "{extra[serialized]},\n"


def create_logger() -> logger:
    """Create custom logger."""
    logger.remove()
    # Datadog
    logger.add(
        stdout,
        format=formatter,
        level="INFO",
    )
    logger.add(
        stderr,
        format=formatter,
        level="ERROR",
    )
    logger.add(
        stdout,
        colorize=True,
        level="INFO",
        catch=True,
        format="<light-cyan>{time:MM-DD-YYYY HH:mm:ss}</light-cyan> | "
               + "<light-green>{level}</light-green>: "
               + "<light-white>{message}</light-white>"
    )
    if Config.FLASK_ENV == 'production':
        logger.add(
            'logs/errors.log',
            colorize=True,
            level="ERROR",
            rotation="200 MB",
            format="<light-cyan>{time:MM-DD-YYYY HH:mm:ss}</light-cyan> <light-red>{level}</light-red>:<light-white>{message}</light-white>"
        )
        # Datadog
        logger.add(
            'logs/info.json',
            format=formatter,
            level="INFO",
            rotation="500 MB",
        )
        logger.add(
            'logs/errors.json',
            format=formatter,
            level="ERROR",
            rotation="500 MB",
        )
        # APM
        apm_format = ('%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] '
                      '[dd.service=%(dd.service)s dd.env=%(dd.env)s dd.version=%(dd.version)s dd.trace_id=%(dd.trace_id)s dd.span_id=%(dd.span_id)s] '
                      '- %(message)s')
        logger.add(
            'logs/apm.json',
            format=apm_format,
            level="INFO",
            rotation="500 MB",
        )
    return logger


LOGGER = create_logger()
