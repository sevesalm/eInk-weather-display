from PIL import Image, ImageDraw, ImageOps
import logging
import utils

def get_battery_icon(voltage, images):
  if (voltage >= 2900):
    return images['misc']['battery_full']
  if (voltage >= 2700):
    return images['misc']['battery_75']
  if (voltage >= 2500):
    return images['misc']['battery_50']
  if (voltage >= 2300):
    return images['misc']['battery_25']
  return images['misc']['battery_empty']

def get_sensor_panel(images, fonts, config):
  logger = logging.getLogger(__name__)
  logger.info('Generating sensor panel')

  x_size = 600
  y_size = 300

  image = Image.new('L', (x_size, y_size), 0xff) 
  draw = ImageDraw.Draw(image)
  
  utils.draw_title(draw, (120, 80), 'IN', fonts)

  logger.info('Fetching sensor data')
  sensor_mac = config.get('RUUVITAG_MAC_IN')
  try:
    if (not config.getboolean('FILE_OUTPUT')):
      from ruuvitag_sensor.ruuvi_rx import RuuviTagReactive
      import rx
      ruuvi_reactive = RuuviTagReactive([sensor_mac])
      sensor_data = ruuvi_reactive\
        .get_subject()\
        .map(lambda x: {x[0]: x[1]})\
        .merge(rx.Observable.timer(config.getint('SENSOR_POLL_TIMEOUT')).map(lambda x: {}))\
        .to_blocking()\
        .first()
      ruuvi_reactive.stop() 
      logger.info('Received data: %s', repr(sensor_data))
    else:
      sensor_data = {sensor_mac: {"temperature": 22.7, "humidity": 46.7, "battery": 2350}}
      logger.info('Using fake data: %s', repr(sensor_data))
  except Exception as e:
    logger.error('get_data_for_sensors() failed: %s', repr(e))
    sensor_data = {}

  if (sensor_mac in sensor_data):
    data_y_base = 150
    state_in = sensor_data[sensor_mac]
    utils.draw_quantity(draw, (x_size//2 + 150, data_y_base), str(round(state_in['temperature'], 1)), '°C', fonts, 'font_lg', 'font_sm')
    utils.draw_quantity(draw, (x_size//2 + 150, data_y_base + 90), str(round(state_in['humidity'])), '%', fonts, 'font_sm')
    battery_icon = get_battery_icon(state_in['battery'], images)
    image.paste(battery_icon, (10, 80), ImageOps.invert(battery_icon))
  else: 
    logger.info(f'Could not find mac {sensor_mac} in sensor data')
    no_wifi_image = images['misc']['no_wifi']
    image.paste(no_wifi_image, (x_size//2 - no_wifi_image.width//2, y_size//2 - no_wifi_image.height//2), ImageOps.invert(no_wifi_image))
  
  # Borders
  if (config.getboolean('DRAW_PANEL_BORDERS')):
    draw.polygon([(0, 0), (x_size-1, 0), (x_size-1, y_size-1), (0, y_size-1), (0, 0)])
  
  return image