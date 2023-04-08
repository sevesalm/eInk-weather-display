import logging
import LogFormatter

DEFAULT_FILENAME = 'logger.log'


def set_module_log_levels() -> None:
    logging.getLogger('ruuvitag_sensor').setLevel(logging.INFO)
    logging.getLogger('PIL').setLevel(logging.INFO)
    logging.getLogger('Rx').setLevel(logging.INFO)


def setup(loglevel=logging.DEBUG) -> None:
    set_module_log_levels()
    fileHandler = logging.FileHandler(DEFAULT_FILENAME)
    fileHandler.setLevel(logging.WARN)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(loglevel)
    stream_handler.setFormatter(LogFormatter.LogFormatter())
    handlers = [fileHandler, stream_handler]

    logging.basicConfig(
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
        level=logging.DEBUG
    )
