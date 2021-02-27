import logging

DEFAULT_FILENAME = 'logger.log'

def get_logger(name, filename = DEFAULT_FILENAME):
  logger = logging.getLogger(name)

  # Check if this logger already has been configured
  if(not logger.hasHandlers()):
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler('logger.log')
    file_handler.setLevel(logging.WARN)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

  return logger