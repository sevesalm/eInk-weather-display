#!/usr/bin/python
# -*- coding:utf-8 -*-
import configparser
from PIL import Image, ImageDraw, ImageFont
from apscheduler.schedulers.blocking import BlockingScheduler
import log
import logging
import utils
import epd_utils
from icons import get_weather_images
from observation_panel import get_observation_panel
from forecast_panel import get_forecasts_panel
from celestial_panel import get_celestial_panel
from info_panel import get_info_panel
from sensor_panel import get_sensor_panel

fonts = {
  'font_lg': ImageFont.truetype('fonts/FiraSansCondensed-400.woff', 32),
  'font_sm': ImageFont.truetype('fonts/FiraSansCondensed-400.woff', 18),
  'font_sm_bold': ImageFont.truetype('fonts/FiraSansCondensed-700.woff', 18),
  'font_xs': ImageFont.truetype('fonts/FiraSansCondensed-400.woff', 14),
  'font_weather_m': ImageFont.truetype('fonts/weathericons-regular-webfont.woff', 52)
}

def main_loop(epd, observation_images, forecast_images, misc_images, config):
  logger = logging.getLogger(__name__)
  logger.info('Refresh started')
  full_image = Image.new('L', (epd.height, epd.width), 0xff)
  draw = ImageDraw.Draw(full_image)

  # Draw individual panels
  logger.info('Drawing panels')
  observation_panel = get_observation_panel(config['FMI_LOCATION'], observation_images, misc_images, fonts, config)
  info_panel = get_info_panel(fonts, config)
  (forecasts_panel, first_position) = get_forecasts_panel(forecast_images, misc_images, fonts, config)
  celestial_panel = get_celestial_panel(first_position, misc_images, fonts, config)
  sensor_panel = get_sensor_panel(fonts, config)

  # Paste the panels on the main image
  logger.info('Pasting panels')
  full_image.paste(observation_panel, (0, 0))
  full_image.paste(celestial_panel, (observation_panel.width, 30))
  full_image.paste(forecasts_panel, (0, observation_panel.height))
  full_image.paste(info_panel, (epd.height - info_panel.width, 0))
  full_image.paste(sensor_panel, (observation_panel.width + celestial_panel.width, 30))

  if(config.get('DRAW_BORDERS')):
    draw.line([20, observation_panel.height, full_image.width - 20, observation_panel.height], fill=0xC0)
    draw.line([observation_panel.width, 20, observation_panel.width, observation_panel.height - 20], fill=0xC0)

  logger.info('Sending image to EPD')
  epd.init(0)
  epd.display_4Gray(epd.getbuffer_4Gray(full_image))
  epd.sleep()
  logger.info('Refresh complete')

def main():
  log.setup()
  logger = logging.getLogger(__name__)
  logger.info("App starting")
  try:
    utils.check_python_version()
    config_parser = configparser.ConfigParser()
    config_parser.read('../config.ini')
    config = config_parser['general']
    (observation_images, forecast_images, misc_images) = get_weather_images(config)
    epd = epd_utils.get_epd()
    epd_utils.epd_init(epd) 
    logger.info("Initial refresh")
    main_loop(epd, observation_images, forecast_images, misc_images, config) # Once in the beginning

    logger.info('Starting scheduler')
    scheduler = BlockingScheduler()
    scheduler.add_job(lambda: main_loop(epd, observation_images, forecast_images, misc_images, config), 'cron', minute='5/10')
    scheduler.start()
    epd_utils.epd_exit(epd) 

  except KeyboardInterrupt:    
    logger.warning("KeyboardInterrupt error")
    epd_utils.epd_exit(epd) 

  except Exception as e:
    logger.exception('Unexpected error')

if __name__ == "__main__":
  main()