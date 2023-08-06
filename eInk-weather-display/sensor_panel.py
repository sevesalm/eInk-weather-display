from configparser import SectionProxy
from typing import Optional
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


def get_signal_strength_icon(rssi: float, images: Icons) -> Image.Image:
  if (rssi > -50):
    return images['misc']['signal_high']
  if (rssi > -75):
    return images['misc']['signal_med']
  return images['misc']['signal_low']


def get_sensor_panel(sensor_mac: str, sub_title: Optional[str], sensor_data: SensorData, images: Icons, fonts: Fonts, config: SectionProxy) -> Image.Image:
  logger = logging.getLogger(__name__)
  logger.info('Generating sensor panel')

  x_size = 380
  y_size = 330 if (sub_title) else 230
  offset = 100

  image = Image.new('L', (x_size, y_size), 0xff)
  draw = ImageDraw.Draw(image)

  if (sub_title):
    utils.draw_title(draw, fonts['font_sm'], 'SENSOR', sub_title, fonts['font_xxs'])

  if (sensor_mac in sensor_data):
    data_y_base = 100 if (sub_title) else 0
    state_in = sensor_data[sensor_mac]

    # Temperature
    utils.draw_quantity(draw, (x_size//2 + offset, data_y_base + 120), utils.roundToString(state_in['temperature'], 1), '°C', fonts, 'font_lg', 'font_sm')

    # Battery level
    battery_icon = icons.get_scaled_image(get_battery_icon(state_in['battery'], images), 60)
    image.paste(battery_icon, (x_size//2 + offset + 10, data_y_base - 10), battery_icon)

    # Humidity
    humidity_icon = icons.get_scaled_image(images['misc']['humidity'], 70)
    image.paste(humidity_icon, (x_size//2 + offset - 140, data_y_base + 140), humidity_icon)
    utils.draw_quantity(draw, (x_size//2 + offset, data_y_base + 200), utils.roundToString(state_in['humidity']), '%', fonts)

    # Signal strength
    signal_strength_icon = icons.get_scaled_image(get_signal_strength_icon(state_in['rssi'], images), 70)
    image.paste(signal_strength_icon, (x_size//2 + offset - 250, data_y_base + 140), signal_strength_icon)
  else:
    logger.info(f'Could not find mac {sensor_mac} in sensor data')
    no_signal_icon = icons.get_scaled_image(images['misc']['no_signal'], 150)
    image.paste(no_signal_icon, (x_size//2 - no_signal_icon.width//2, y_size//2 - no_signal_icon.height//2), no_signal_icon)

  # Borders
  if (config.getboolean('DRAW_PANEL_BORDERS')):
    draw.polygon([(0, 0), (x_size-1, 0), (x_size-1, y_size-1), (0, y_size-1), (0, 0)])

  return image
