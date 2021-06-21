import ctypes
import logging
from PIL import Image, ImageDraw
from observation_panel import get_observation_panel
from info_panel import get_info_panel
from forecast_panel import get_forecasts_panel
from celestial_panel import get_celestial_panel
from sensor_panel import get_sensor_panel

def refresh(panel_size, fonts, images, config, epd_so, init):
  logger = logging.getLogger(__name__)
  if (init == True):
    logger.info('Full refresh started')
  else:
    logger.info('Partial refresh started')
  full_image = Image.new('L', (panel_size[0], panel_size[1]), 0xff)
  draw = ImageDraw.Draw(full_image)

  # Draw individual panels
  logger.info('Drawing panels')
  observation_panel = get_observation_panel(config['FMI_LOCATION'], images, fonts, config)
  sensor_panel_in = get_sensor_panel(config.get('RUUVITAG_MAC_IN'), config.get('RUUVITAG_MAC_IN_NAME'), images, fonts, config)
  sensor_panel_out = get_sensor_panel(config.get('RUUVITAG_MAC_OUT'), config.get('RUUVITAG_MAC_OUT_NAME'), images, fonts, config, False)
  (forecasts_panel, first_position) = get_forecasts_panel(images, fonts, config)
  celestial_panel = get_celestial_panel(first_position, images, fonts, config)
  info_panel = get_info_panel(fonts, config)

  # Paste the panels on the main image
  logger.info('Pasting panels')
  full_image.paste(observation_panel, (0, 0))
  full_image.paste(sensor_panel_in, (observation_panel.width, 0))
  full_image.paste(sensor_panel_out, (observation_panel.width, sensor_panel_in.height))
  full_image.paste(forecasts_panel, (0, panel_size[1] - forecasts_panel.height))
  full_image.paste(celestial_panel, (observation_panel.width + sensor_panel_in.width, 0))
  full_image.paste(info_panel, (panel_size[0] - info_panel.width, 0))

  if(config.getboolean('DRAW_BORDERS')):
    border_color = 0x80
    draw_width = 2 
    draw.line([0, panel_size[1] - forecasts_panel.height, panel_size[0], panel_size[1] - forecasts_panel.height], fill=border_color, width=draw_width)
    draw.line([observation_panel.width, 0, observation_panel.width, observation_panel.height - panel_size[1]//20], fill=border_color, width=draw_width)
    draw.line([observation_panel.width + sensor_panel_in.width, 0, observation_panel.width + sensor_panel_in.width, observation_panel.height - panel_size[1]//20], fill=border_color, width=draw_width)
    draw.line([observation_panel.width + sensor_panel_in.width + celestial_panel.width, 0, observation_panel.width + sensor_panel_in.width + celestial_panel.width, observation_panel.height - panel_size[1]//20], fill=border_color, width=draw_width)
  
  if (config.getboolean('FILE_OUTPUT')):
    filename = config.get('OUTPUT_FILENAME')
    logger.info(f'Saving image to {filename}')
    full_image.save(filename)
  else:
    logger.info('Sending image to EPD')
    image_bytes = full_image.rotate(0 if not config.getboolean('ROTATE_180') else 180, expand=True).tobytes()
    c_logger = ctypes.CFUNCTYPE(None, ctypes.c_int, ctypes.c_wchar_p)(logging.getLogger('esp.so').log)
    epd_so.draw_image_8bit(image_bytes, ctypes.c_bool(init), config.getint('BITS_PER_PIXEL'), c_logger)
  logger.info('Refresh complete')