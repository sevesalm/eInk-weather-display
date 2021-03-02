from PIL import Image, ImageDraw
import logging
from ruuvitag_sensor.ruuvi import RuuviTagSensor
import utils

def get_sensor_panel(fonts, config):
  logger = logging.getLogger(__name__)
  logger.info('Generating sensor panel')

  x_size = 90
  y_size = 70

  image = Image.new('L', (x_size, y_size), 0xff) 
  draw = ImageDraw.Draw(image)

  logger.info('Fetching sensor data')
  sensor_data = RuuviTagSensor.get_data_for_sensors([config.get('MAC_IN')], 5)
  logger.info(sensor_data)

  if (config.get('MAC_IN') in sensor_data):
    state_in = sensor_data[config.get('MAC_IN')]
    draw.text((x_size/2, 0), 'In', font = fonts['font_sm'], fill = 0, anchor = 'ma')
    utils.draw_quantity(draw, (x_size/2, 35), str(round(state_in['temperature'], 1)), '°C', fonts, 'font_sm')
    utils.draw_quantity(draw, (x_size/2, 55), str(round(state_in['humidity'], 1)), '%', fonts, 'font_sm')
  
  return image