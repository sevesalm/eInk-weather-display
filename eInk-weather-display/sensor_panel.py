import random
from PIL import Image, ImageDraw
from ruuvitag_sensor.ruuvi_rx import RuuviTagReactive
import rx
import logging
import utils
import icons

def get_battery_icon(voltage, images):
  if (voltage >= 2850):
    return images['misc']['battery_full']
  if (voltage >= 2750):
    return images['misc']['battery_75']
  if (voltage >= 2600):
    return images['misc']['battery_50']
  if (voltage >= 2400):
    return images['misc']['battery_25']
  return images['misc']['battery_empty']

def get_sensor_panel(sensor_mac, sensor_name, images, fonts, config, draw_title = True):
  logger = logging.getLogger(__name__)
  logger.info('Generating sensor panel')

  x_size = 550
  y_size = 330

  image = Image.new('L', (x_size, y_size), 0xff) 
  draw = ImageDraw.Draw(image)
  
  if (draw_title):
    utils.draw_title(draw, fonts['font_sm'], 'SENSOR', sensor_name, fonts['font_xs'])

  try:
    if (not config.getboolean('USE_FAKE_SENSOR_DATA')):
      timeout = config.getint('SENSOR_POLL_TIMEOUT')
      logger.info(f'Fetching sensor data (timeout: {timeout})')
      ruuvi_reactive = RuuviTagReactive([sensor_mac])
      sensor_data = ruuvi_reactive\
        .get_subject()\
        .map(lambda x: {x[0]: x[1]})\
        .merge(rx.Observable.timer(timeout).map(lambda x: {}))\
        .to_blocking()\
        .first()
      ruuvi_reactive.stop() 
      logger.info('Received data: %s', repr(sensor_data))
    else:
      sensor_data = {sensor_mac: {"temperature": random.uniform(18, 30), "humidity": random.uniform(20, 80), "battery": random.uniform(2000, 3000), "rssi": random.uniform(-120, -10)}}
      logger.info('Using fake data: %s', repr(sensor_data))
  except Exception as e:
    logger.error('get_data_for_sensors() failed: %s', repr(e))
    sensor_data = {}

  if (sensor_mac in sensor_data):
    data_y_base = 100 if (draw_title) else 0 
    state_in = sensor_data[sensor_mac]
    utils.draw_quantity(draw, (x_size//2 + 160, data_y_base + 120), str(round(state_in['temperature'], 1)), '°C', fonts, 'font_lg', 'font_sm')
    utils.draw_quantity(draw, (x_size//2 + 160, data_y_base + 210), str(round(state_in['humidity'])), '%', fonts)

    # Battery level
    battery_icon = icons.get_scaled_image(get_battery_icon(state_in['battery'], images), 120)
    image.paste(battery_icon, (30, data_y_base - 30), battery_icon)
    utils.draw_quantity(draw, (130, data_y_base + 125), str(round(state_in['battery']/1000, 2)), 'V', fonts, 'font_xs', 'font_xxs')

    # RSSI - not yet part of ruuvitag-sensor
    # Adding is trivial by editing ruuvitag-sensor package's decoder.py
    # See: https://github.com/ttu/ruuvitag-sensor/issues/52
    if ('rssi' in state_in):
      utils.draw_quantity(draw, (130, data_y_base + 190), str(round(state_in['rssi'])), 'dBm', fonts, 'font_xs', 'font_xxs')

  else: 
    logger.info(f'Could not find mac {sensor_mac} in sensor data')
    no_wifi_image = icons.get_scaled_image(images['misc']['no_wifi'], 200)
    image.paste(no_wifi_image, (x_size//2 - no_wifi_image.width//2, y_size//2 - no_wifi_image.height//2), no_wifi_image)
  
  # Borders
  if (config.getboolean('DRAW_PANEL_BORDERS')):
    draw.polygon([(0, 0), (x_size-1, 0), (x_size-1, y_size-1), (0, y_size-1), (0, 0)])
  
  return image