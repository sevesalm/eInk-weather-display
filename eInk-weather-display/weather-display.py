#!/usr/bin/python
# -*- coding:utf-8 -*-
import configparser
import datetime
from PIL import ImageFont
from apscheduler.schedulers.blocking import BlockingScheduler
import log
import logging
import ctypes
import utils
import epd_utils
from icons import get_weather_images
import refresh

fonts = {
  'font_lg': ImageFont.truetype('fonts/FiraSansCondensed-400.woff', 32),
  'font_sm': ImageFont.truetype('fonts/FiraSansCondensed-400.woff', 18),
  'font_sm_bold': ImageFont.truetype('fonts/FiraSansCondensed-700.woff', 18),
  'font_xs': ImageFont.truetype('fonts/FiraSansCondensed-400.woff', 14),
  'font_weather_m': ImageFont.truetype('fonts/weathericons-regular-webfont.woff', 52)
}

def main_loop(epd, fonts, observation_images, forecast_images, misc_images, config, epd_so):
  logger = logging.getLogger(__name__)
  logger.info("main_loop() started")
  wakeup_time = datetime.datetime.now()
  if((wakeup_time.minute - 5) % 10 == 0):
    refresh.full(epd, fonts, observation_images, forecast_images, misc_images, config, epd_so)
  else:
    refresh.partial()

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

    (observation_images, forecast_images, misc_images) = get_weather_images(config)
    epd = epd_utils.get_epd()
    if(not config.getboolean('USE_C_LIBRARY')):
      epd_utils.epd_init(epd) 

    logger.info('Import epd.so')
    epd_so = ctypes.CDLL("lib/epd.so")

    logger.info("Initial refresh")
    refresh.full(epd, fonts, observation_images, forecast_images, misc_images, config, epd_so) # Once in the beginning

    logger.info('Starting scheduler')
    scheduler = BlockingScheduler()
    scheduler.add_job(lambda: main_loop(epd, fonts, observation_images, forecast_images, misc_images, config, epd_so), 'cron', minute='5/1')
    scheduler.start()
    epd_utils.epd_exit(epd) 

  except KeyboardInterrupt:    
    logger.warning("KeyboardInterrupt error")
    epd_utils.epd_exit(epd) 

  except Exception as e:
    logger.exception('Unexpected error')

if __name__ == "__main__":
  main()