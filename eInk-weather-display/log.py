import logging

DEFAULT_FILENAME = 'logger.log'

def set_module_log_levels():
    logging.getLogger('ruuvitag_sensor').setLevel(logging.INFO)
    logging.getLogger('PIL').setLevel(logging.INFO)

def setup(loglevel = logging.DEBUG):
    set_module_log_levels()
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