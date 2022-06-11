from configparser import SectionProxy
import random
from PIL import Image, ImageDraw
from ruuvitag_sensor.ruuvi_rx import RuuviTagReactive
from reactivex import operators as ops
import logging
import utils
import icons
from typing import TypedDict, Mapping
from type_alias import Fonts, Icons


class SingleSensorData(TypedDict):
  temperature: float
  humidity: float
  battery: float
  rssi: float


SensorData = Mapping[str, SingleSensorData]


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


def get_sensor_data(logger: logging.Logger, config: SectionProxy, macs: list[str]) -> SensorData:
  try:
    if (not config.getboolean('USE_FAKE_SENSOR_DATA')):
      ruuvis = RuuviTagReactive(macs)
      ruuvi_emissions = ruuvis.get_subject()
      missing_data = ruuvi_emissions.pipe(
                        ops.map(lambda x: x[0]),  # Only the mac address
                        ops.buffer_with_time(config.getint('SENSOR_POLL_TIMEOUT')),  # Buffer for some time
                        ops.map(lambda x: set(x)),  # Convert macs into a set
                        ops.first(),
                        ops.flat_map(lambda x: list(set(macs).difference(x))),  # type: ignore # Emit once per each missing mac
                        ops.map(lambda x: (x, None))
                      )

      sensor_data = ruuvi_emissions.pipe(
                      ops.merge(missing_data),
                      ops.scan(lambda acc, x: acc | {x[0]: x[1]}, {}),
                      ops.filter(lambda x: len(x.keys()) == len(macs)),
                      ops.first()
                    ).run()

      ruuvis.stop()
      logger.info('Sensor data received: %s', repr(sensor_data))
      return {k: v for k, v in sensor_data.items() if v is not None}
    else:
      sensor_data: SensorData = {mac: {"temperature": random.uniform(18, 30), "humidity": random.uniform(20, 80), "battery": random.uniform(2000, 3000), "rssi": random.uniform(-120, -10)} for mac in macs}
      logger.info('Using fake data: %s', repr(sensor_data))
      return sensor_data
  except Exception as e:
    logger.error('get_sensor_data() failed: %s', repr(e))
    return {}


def get_sensor_panel(sensor_mac: str, sensor_name: str, sensor_data: SensorData, images: Icons, fonts: Fonts, config: SectionProxy, draw_title: bool = True) -> Image.Image:
  logger = logging.getLogger(__name__)
  logger.info('Generating sensor panel')

  x_size = 400
  y_size = 330

  image = Image.new('L', (x_size, y_size), 0xff)
  draw = ImageDraw.Draw(image)

  if (draw_title):
    utils.draw_title(draw, fonts['font_sm'], 'SENSOR', sensor_name, fonts['font_xs'])

  if (sensor_mac in sensor_data):
    data_y_base = 100 if (draw_title) else 0
    state_in = sensor_data[sensor_mac]
    utils.draw_quantity(draw, (x_size//2 + 110, data_y_base + 120), str(round(state_in['temperature'], 1)), '°C', fonts, 'font_lg', 'font_sm')
    humidity_icon = icons.get_scaled_image(images['misc']['humidity'], 70)
    image.paste(humidity_icon, (x_size//2 - 50, data_y_base + 150), humidity_icon)
    utils.draw_quantity(draw, (x_size//2 + 110, data_y_base + 210), str(round(state_in['humidity'])), '%', fonts)

    # Battery level
    battery_icon = icons.get_scaled_image(get_battery_icon(state_in['battery'], images), 60)
    image.paste(battery_icon, (x_size//2 + 120, data_y_base - 10), battery_icon)

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
