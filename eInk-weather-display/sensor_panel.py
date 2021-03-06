from PIL import Image, ImageDraw, ImageOps
import logging
from ruuvitag_sensor.ruuvi import RuuviTagSensor
import utils

def get_sensor_panel(misc_images, fonts, config):
  logger = logging.getLogger(__name__)
  logger.info('Generating sensor panel')

  x_size = 100
  y_size = 100

  image = Image.new('L', (x_size, y_size), 0xff) 
  draw = ImageDraw.Draw(image)

  logger.info('Fetching sensor data')
  try:
    sensor_data = RuuviTagSensor.get_data_for_sensors([config.get('RUUVITAG_MAC_IN')], config.getint('SENSOR_POLL_TIMEOUT'))
  except e:
    logger.error('get_data_for_sensors() failed %s', repr(e))
    sensor_data = {}
  logger.info('Received data: %s', repr(sensor_data))

  if (config.get('RUUVITAG_MAC_IN') in sensor_data):
    state_in = sensor_data[config.get('RUUVITAG_MAC_IN')]
    # draw.text((x_size/2, 0), 'In', font = fonts['font_sm'], fill = 0, anchor = 'ma')
    utils.draw_quantity(draw, (x_size//2 + 15, 20), str(round(state_in['temperature'], 1)), '°C', fonts, 'font_lg')
    utils.draw_quantity(draw, (x_size//2 + 15, 45), str(round(state_in['humidity'], 1)), '%', fonts, 'font_sm')
  else: 
    no_wifi_image = misc_images['no_wifi']
    image.paste(no_wifi_image, (x_size//2 - no_wifi_image.width//2, y_size//2 - no_wifi_image.height//2), ImageOps.invert(no_wifi_image))
  
  # Borders
  if (config.getboolean('DRAW_PANEL_BORDERS')):
    draw.polygon([(0, 0), (x_size-1, 0), (x_size-1, y_size-1), (0, y_size-1), (0, 0)])
  
  return image