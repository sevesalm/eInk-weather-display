#!/usr/bin/python
# -*- coding:utf-8 -*-
import configparser
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
import log
import logging
import ctypes
import utils
from icons import get_weather_images
import refresh

def main_loop(panel_size, fonts, images, config, epd_so):
  logger = logging.getLogger(__name__)
  logger.info("main_loop() started")
  wakeup_time = datetime.datetime.now()
  if((wakeup_time.minute - 5) % config.getint('REFRESH_FULL_INTERVAL') == 0):
    refresh.refresh(panel_size, fonts, images, config, epd_so, True)
  elif(wakeup_time.minute % config.getint('REFRESH_PARTIAL_INTERVAL') == 0):
    refresh.refresh(panel_size, fonts, images, config, epd_so, False)

def main():
  log.setup()
  logger = logging.getLogger(__name__)
  logger.info("App starting")
  try:
    utils.check_python_version()
    config_parser = configparser.ConfigParser()
    config_parser.read('config.ini')
    logger.info('Config: %s', config_parser.items('general'))
    config = config_parser['general']

    fonts = utils.get_fonts(config)
    images = get_weather_images(config)

    logger.info('Import epd control library')
    (epd_so, panel_size) = utils.get_epd_data(config)

    logger.info("Initial refresh")
    refresh.refresh(panel_size, fonts, images, config, epd_so, True) # Once in the beginning

    logger.info('Starting scheduler')
    scheduler = BlockingScheduler()
    scheduler.add_job(lambda: main_loop(panel_size, fonts, images, config, epd_so), 'cron', minute='*/1')
    scheduler.start()

  except KeyboardInterrupt:    
    logger.warning("KeyboardInterrupt error")

  except Exception as e:
    logger.exception('Unexpected error')

if __name__ == "__main__":
  main()