from PIL import Image, ImageDraw, ImageOps
import logging
from ruuvitag_sensor.ruuvi import RuuviTagSensor
import utils

def get_sensor_panel(images, fonts, config):
  logger = logging.getLogger(__name__)
  logger.info('Generating sensor panel')

  x_size = 600
  y_size = 300

  image = Image.new('L', (x_size, y_size), 0xff) 
  draw = ImageDraw.Draw(image)
  
  title_size = (120, 80)
  draw.rectangle([(0, 0), (title_size[0], title_size[1])], fill=0x00)
  draw.text((title_size[0]//2, title_size[1]//2), 'IN', fill="white", font=fonts['font_sm'], anchor='mm')

  logger.info('Fetching sensor data')
  try:
    sensor_data = RuuviTagSensor.get_data_for_sensors([config.get('RUUVITAG_MAC_IN')], config.getint('SENSOR_POLL_TIMEOUT'))
  except e:
    logger.error('get_data_for_sensors() failed %s', repr(e))
    sensor_data = {}
  logger.info('Received data: %s', repr(sensor_data))

    utils.draw_quantity(draw, (x_size//2 + 150, data_y_base), str(round(state_in['temperature'], 1)), '°C', fonts, 'font_lg', 'font_sm')
    utils.draw_quantity(draw, (x_size//2 + 150, data_y_base + 90), str(round(state_in['humidity'])), '%', fonts, 'font_sm')
  else: 
    no_wifi_image = images['misc']['no_wifi']
    image.paste(no_wifi_image, (x_size//2 - no_wifi_image.width//2, y_size//2 - no_wifi_image.height//2), ImageOps.invert(no_wifi_image))
  
  # Borders
  if (config.getboolean('DRAW_PANEL_BORDERS')):
    draw.polygon([(0, 0), (x_size-1, 0), (x_size-1, y_size-1), (0, y_size-1), (0, 0)])
  
  return image