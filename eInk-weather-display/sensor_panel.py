from configparser import SectionProxy
from PIL import Image, ImageDraw
import logging
import utils
import icons
from type_alias import Fonts, Icons, SensorData


def get_battery_icon(voltage: float, images: Icons) -> Image.Image:
  if (voltage >= 2850):
    return images['misc']['battery_full']
  if (voltage >= 2750):
    return images['misc']['battery_75']
  if (voltage >= 2600):
    return images['misc']['battery_50']
  if (voltage >= 2400):
    return images['misc']['battery_25']
  return images['misc']['battery_empty']


def get_sensor_panel(sensor_mac: str, sensor_name: str, sensor_data: SensorData, images: Icons, fonts: Fonts, config: SectionProxy, draw_title: bool = True) -> Image.Image:
  logger = logging.getLogger(__name__)
  logger.info('Generating sensor panel')

  x_size = 380
  y_size = 330
  offset = 100

  image = Image.new('L', (x_size, y_size), 0xff)
  draw = ImageDraw.Draw(image)

  if (draw_title):
    utils.draw_title(draw, fonts['font_sm'], 'SENSOR', sensor_name, fonts['font_xxs'])

  if (sensor_mac in sensor_data):
    data_y_base = 100 if (draw_title) else 0
    state_in = sensor_data[sensor_mac]
    utils.draw_quantity(draw, (x_size//2 + offset, data_y_base + 120), utils.roundToString(state_in['temperature'], 1), '°C', fonts, 'font_lg', 'font_sm')
    humidity_icon = icons.get_scaled_image(images['misc']['humidity'], 70)
    image.paste(humidity_icon, (x_size//2 + offset - 160, data_y_base + 150), humidity_icon)
    utils.draw_quantity(draw, (x_size//2 + offset, data_y_base + 210), utils.roundToString(state_in['humidity']), '%', fonts)

    # Battery level
    battery_icon = icons.get_scaled_image(get_battery_icon(state_in['battery'], images), 60)
    image.paste(battery_icon, (x_size//2 + offset + 10, data_y_base - 10), battery_icon)

    # RSSI - not yet part of ruuvitag-sensor
    # Adding is trivial by editing ruuvitag-sensor package's decoder.py
    # See: https://github.com/ttu/ruuvitag-sensor/issues/52
    # if ('rssi' in state_in):
    #   utils.draw_quantity(draw, (100, data_y_base + 210), utils.roundToString(state_in['rssi']), 'dBm', fonts, 'font_xs', 'font_xxs')

  else:
    logger.info(f'Could not find mac {sensor_mac} in sensor data')
    no_wifi_image = icons.get_scaled_image(images['misc']['no_wifi'], 200)
    image.paste(no_wifi_image, (x_size//2 - no_wifi_image.width//2, y_size//2 - no_wifi_image.height//2), no_wifi_image)

  # Borders
  if (config.getboolean('DRAW_PANEL_BORDERS')):
    draw.polygon([(0, 0), (x_size-1, 0), (x_size-1, y_size-1), (0, y_size-1), (0, 0)])

  return image
