import logging
import http.client
import logging
import os.path

DEFAULT_FILENAME = 'logger.log'

def setup(loglevel = logging.DEBUG):
    bleson_logger = logging.getLogger('bleson')
    bleson_logger.setLevel(logging.ERROR)
    fileHandler = logging.FileHandler(DEFAULT_FILENAME)
    fileHandler.setLevel(logging.WARN)
    handlers = [fileHandler]

    if loglevel is not None:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(loglevel)
        handlers.append(stream_handler)

    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(
        format=log_format, datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers, level=logging.DEBUG
    )