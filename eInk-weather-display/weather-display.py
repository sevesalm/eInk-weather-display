#!/usr/bin/python
# -*- coding:utf-8 -*-
import configparser
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
import log
import logging
import utils
from icons import get_weather_images
import refresh
import ctypes
from typing import Optional
from type_alias import Icons, Fonts

CONFIG_FILENAME = 'config.ini'


def main_loop(panel_size: tuple[int, int], fonts: Fonts, images: Icons, config: configparser.SectionProxy, epd_so: Optional[ctypes.CDLL]) -> None:
  logger = logging.getLogger(__name__)
  logger.info("main_loop() started")
  wakeup_time = datetime.datetime.now()
  if ((wakeup_time.minute - 5) % config.getint('REFRESH_FULL_INTERVAL') == 0):
    refresh.refresh(panel_size, fonts, images, config, epd_so, True)
  elif (wakeup_time.minute % config.getint('REFRESH_PARTIAL_INTERVAL') == 0):
    refresh.refresh(panel_size, fonts, images, config, epd_so, False)


def main():
  log.setup()
  logger = logging.getLogger(__name__)
  logger.info("App starting")
  try:
    utils.check_python_version()
    utils.check_raqm_support(logger)
    logger.info(f'Reading config file "{CONFIG_FILENAME}"')
    with open(CONFIG_FILENAME) as f:
      config_parser = configparser.ConfigParser()
      config_parser.read_file(f)
      logger.info('Config: %s', config_parser.items('general'))
      config = config_parser['general']

      fonts = utils.get_fonts(config)
      images = get_weather_images()

      logger.info('Import epd control library')
      (epd_so, panel_size) = utils.get_epd_data(config)

      logger.info("Initial refresh")
      refresh.refresh(panel_size, fonts, images, config, epd_so, True)  # Once in the beginning

      if not config.getboolean('DEV_MODE'):
        logger.info('Starting scheduler')
        scheduler = BlockingScheduler()
        scheduler.add_job(lambda: main_loop(panel_size, fonts, images, config, epd_so), 'cron', minute='*/1')
        scheduler.start()

  except FileNotFoundError as e:
    logger.exception(f'Error opening file "{CONFIG_FILENAME}": %s', str(e))

  except KeyboardInterrupt:
    logger.warning("KeyboardInterrupt error")

  except Exception as e:
    logger.exception('Unexpected error: %s', str(e))


if __name__ == "__main__":
  main()
