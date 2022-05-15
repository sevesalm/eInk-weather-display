from lib import epd3in7
import logging


def get_epd():
  return epd3in7.EPD()


def epd_init(epd):
  logger = logging.getLogger(__name__)
  logger.info("Initializing EPD")
  epd.init(0)
  epd.Clear(0xff, 0)


def epd_exit(epd):
  logger = logging.getLogger(__name__)
  logger.info("Exiting EPD")
  epd.sleep()
  epd.Dev_exit()
