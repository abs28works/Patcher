from sys import stdout

from loguru import logger as custom_logger


def formatter(log: dict) -> str:
    """
    Format log colors based on level.
    :param log: Logged event stored as map containing contextual metadata.
    :type log: dict
    :returns: str
    """
    if log["level"].name == "WARNING":
        return (
            "<light-cyan>{time:MM-DD-YYYY HH:mm:ss}</light-cyan> | "
            "<light-yellow>{level}</light-yellow>: "
            "<light-white>{message}</light-white> \n"
        )
    elif log["level"].name == "ERROR":
        return (
            "<light-cyan>{time:MM-DD-YYYY HH:mm:ss}</light-cyan> | "
            "<light-red>{level}</light-red>: "
            "<light-white>{message}</light-white> \n"
        )
    else:
        return (
            "<light-cyan>{time:MM-DD-YYYY HH:mm:ss}</light-cyan> | "
            "<light-white>{level}</light-white>: "
            "<light-white>{message}</light-white> \n"
        )


def create_logger() -> custom_logger:
    custom_logger.remove()
    custom_logger.add(stdout, colorize=True, format=formatter)
    return custom_logger


LOGGER = create_logger()