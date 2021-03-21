import ctypes
import logging
from PIL import Image, ImageDraw
from observation_panel import get_observation_panel
from info_panel import get_info_panel
from forecast_panel import get_forecasts_panel
from celestial_panel import get_celestial_panel
from sensor_panel import get_sensor_panel
import utils

def full(epd, fonts, images, config, epd_so):
  logger = logging.getLogger(__name__)
  logger.info('Full refresh started')
  full_image = Image.new('L', (epd.height, epd.width), 0xff)
  draw = ImageDraw.Draw(full_image)

  # Draw individual panels
  logger.info('Drawing panels')
  observation_panel = get_observation_panel(config['FMI_LOCATION'], images, fonts, config)
  info_panel = get_info_panel(fonts, config)
  (forecasts_panel, first_position) = get_forecasts_panel(images, fonts, config)
  celestial_panel = get_celestial_panel(first_position, images, fonts, config)
  sensor_panel = get_sensor_panel(images, fonts, config)

  # Paste the panels on the main image
  logger.info('Pasting panels')
  full_image.paste(observation_panel, (0, 0))
  full_image.paste(sensor_panel, (observation_panel.width, 0))
  full_image.paste(celestial_panel, (observation_panel.width + sensor_panel.width, 30))
  full_image.paste(forecasts_panel, (0, observation_panel.height))
  full_image.paste(info_panel, (epd.height - info_panel.width, 0))

  if(config.get('DRAW_BORDERS')):
    border_color = 0x80 if not config.getboolean('ENABLE_1BIT_MODE') else 0x00
    draw.line([20, observation_panel.height, full_image.width - 20, observation_panel.height], fill=border_color)
    draw.line([observation_panel.width, 20, observation_panel.width, observation_panel.height - 20], fill=border_color)

  logger.info('Sending image to EPD')
  if (config.getboolean('USE_C_LIBRARY')):
    if(config.getboolean('ENABLE_1BIT_MODE')):
      image_bytes = full_image.rotate(90 if not config.getboolean('ROTATE_180') else 270, expand=True).convert(mode='1', dither=Image.NONE).tobytes()
      epd_so.draw_image_1bit(image_bytes, ctypes.CFUNCTYPE(None, ctypes.c_int, ctypes.c_wchar_p)(logging.getLogger('esp.so').log))
    else:
      image_bytes = utils.from_8bit_to_2bit(full_image.rotate(90 if not config.getboolean('ROTATE_180') else 270, expand=True))
      epd_so.draw_image_2bit(image_bytes, ctypes.CFUNCTYPE(None, ctypes.c_int, ctypes.c_wchar_p)(logging.getLogger('esp.so').log))
  else:
    epd.display_4Gray(epd.getbuffer_4Gray(full_image))
    epd.sleep()
  logger.info('Saving to image.bmp')
  logger.info('Refresh complete')

def partial():
  logger = logging.getLogger(__name__)
  logger.info('Partial refresh - skipping (not implemented)')