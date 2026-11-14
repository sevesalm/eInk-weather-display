from typing import Optional
from uuid import UUID
from PIL import Image, ImageDraw
import logging
import utils
from type_alias import Fonts
from app_config import AppConfig
from home_assistant import SensorReading


def get_sensor_panel_new(home_assistant_sensor_data: dict[UUID, Optional[SensorReading]], fonts: Fonts, config: AppConfig) -> Image.Image:
  logger = logging.getLogger(__name__)
  logger.info('Generating new sensor panel')

  x_size = 380
  # Fits above the forecast panel (1404 - 720) and leaves room for 6 rows
  y_size = 684

  image = Image.new('L', (x_size, y_size), 0xff)
  draw = ImageDraw.Draw(image)

  # Build a mapping from sensor ID to sensor name
  sensor_names: dict[UUID, str] = {
    sensor.id: sensor.name
    for sensor in config.sensors
  }

  y_offset = 20
  row_height = 110

  for sensor_id, reading in home_assistant_sensor_data.items():
    sensor_name = sensor_names.get(sensor_id, str(sensor_id))

    # Draw sensor name
    draw.text((20, y_offset), sensor_name, font=fonts['font_xxs'], fill=0, anchor='lt')

    if reading is not None:
      # Draw temperature and humidity below the name
      value_y = y_offset + 90
      temp_str = utils.roundToString(reading.temperature, 1) if reading.temperature is not None else utils.NAN_SYMBOL
      humidity_str = utils.roundToString(reading.humidity) if reading.humidity is not None else utils.NAN_SYMBOL

      utils.draw_quantity(draw, (132, value_y), temp_str, '°C', fonts)
      utils.draw_quantity(draw, (320, value_y), humidity_str, '%', fonts, font="font_xs", font_unit='font_xxs')

    y_offset += row_height

  # Borders
  if config.draw_panel_borders:
    draw.polygon([(0, 0), (x_size - 1, 0), (x_size - 1, y_size - 1), (0, y_size - 1), (0, 0)])

  return image


