from lib import epd3in7
from log import get_logger

def get_epd():
  return epd3in7.EPD()

def epd_init(epd):
  logger = get_logger(__name__)
  logger.info("Initializing EPD")
  epd.init(0)
  epd.Clear(0xff, 0)

def epd_exit(epd):
  logger = get_logger(__name__)
  logger.info("Exiting EPD")
  epd.sleep()
  epd.Dev_exit()