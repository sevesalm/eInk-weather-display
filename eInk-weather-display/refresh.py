import ctypes
import logging
from PIL import Image, ImageDraw
from observation_panel import get_observation_panel
from info_panel import get_info_panel
from forecast_panel import get_forecasts_panel
from celestial_panel import get_celestial_panel
from sensor_panel import get_sensor_panel, get_sensor_data
from timeit import default_timer as timer
from configparser import SectionProxy
from typing import Optional
from type_alias import Icons, Fonts
from multiprocessing import Process
from weather import get_observation_data, get_forecast_data

PROCESS_TIMEOPUT = 10  # In seconds


def refresh(panel_size: tuple[int, int], fonts: Fonts, images: Icons, config: SectionProxy, epd_so: Optional[ctypes.CDLL], init: bool) -> None:
  logger = logging.getLogger(__name__)
  logger.info('Refresh started')
  start_time = timer()

  # Fetch data
  start_fetch_time = timer()
  observation_data = get_observation_data(config['FMI_LOCATION'], logger)
  forecast_data = get_forecast_data(config.get('FMI_LOCATION'), 7, 6, logger)
  elapsed_fetch_time = timer() - start_fetch_time

  start_sensor_time = timer()
  sensor_data = get_sensor_data(logger, config, [config.get('RUUVITAG_MAC_IN'), config.get('RUUVITAG_MAC_OUT')])
  elapsed_sensor_time = timer() - start_sensor_time

  # Draw individual panels
  logger.info('Drawing panels')
  start_draw_time = timer()
  observation_panel = get_observation_panel(observation_data, images, fonts, config)
  sensor_panel_in = get_sensor_panel(config.get('RUUVITAG_MAC_IN'), config.get('RUUVITAG_MAC_IN_NAME'), sensor_data, images, fonts, config)
  sensor_panel_out = get_sensor_panel(config.get('RUUVITAG_MAC_OUT'), config.get('RUUVITAG_MAC_OUT_NAME'), sensor_data, images, fonts, config, False)
  (forecasts_panel, position) = get_forecasts_panel(forecast_data, images, fonts, config)
  celestial_panel = get_celestial_panel(position, fonts, config)
  info_panel = get_info_panel(fonts, config)

  # Paste the panels on the main image
  logger.info('Pasting panels')
  full_image = Image.new('L', (panel_size[0], panel_size[1]), 0xff)
  full_image.paste(observation_panel, (0, 0))
  full_image.paste(sensor_panel_in, (observation_panel.width, 0))
  full_image.paste(sensor_panel_out, (observation_panel.width, sensor_panel_in.height))
  full_image.paste(forecasts_panel, (0, panel_size[1] - forecasts_panel.height))
  full_image.paste(celestial_panel, (observation_panel.width + sensor_panel_in.width, 0))
  full_image.paste(info_panel, (panel_size[0] - info_panel.width, 0))
  elapsed_draw_time = timer() - start_draw_time

  if(config.getboolean('DRAW_BORDERS')):
    border_color = 0x80
    draw_width = 2
    draw = ImageDraw.Draw(full_image)
    draw.line([0, panel_size[1] - forecasts_panel.height, panel_size[0], panel_size[1] - forecasts_panel.height], fill=border_color, width=draw_width)
    draw.line([observation_panel.width, 0, observation_panel.width, observation_panel.height - panel_size[1]//20], fill=border_color, width=draw_width)
    draw.line([observation_panel.width + sensor_panel_in.width, 0, observation_panel.width + sensor_panel_in.width, observation_panel.height - panel_size[1]//20], fill=border_color, width=draw_width)
    draw.line([observation_panel.width + sensor_panel_in.width + celestial_panel.width, 0, observation_panel.width + sensor_panel_in.width + celestial_panel.width, observation_panel.height - panel_size[1]//20], fill=border_color, width=draw_width)

  if (config.getboolean('FILE_OUTPUT')):
    filename = config.get('OUTPUT_FILENAME')
    logger.info(f'Saving image to {filename}')
    full_image.save(filename)
    elapsed_refresh_time = 0
  else:
    logger.info(f'Sending image to EPD, {"full" if init else "partial"} refresh')
    if (config.getboolean('MIRROR_HORIZONTAL')):
      full_image = full_image.transpose(Image.FLIP_LEFT_RIGHT)
    image_bytes = full_image.rotate(0 if not config.getboolean('ROTATE_180') else 180, expand=True).tobytes()
    c_logger = ctypes.CFUNCTYPE(None, ctypes.c_int, ctypes.c_wchar_p)(logging.getLogger('esp.so').log)
    if(epd_so):
      start_refresh_time = timer()
      try:
        p = Process(target=epd_so.draw_image_8bit, args=(image_bytes, ctypes.c_bool(init), ctypes.c_int(config.getint('EPD_VOLTAGE')), config.getint('BITS_PER_PIXEL'), c_logger))
        p.start()
        p.join(PROCESS_TIMEOPUT)
        logger.debug(f'Exit code: {p.exitcode}')
        if (p.exitcode is None):
          logger.error('An error occured during draw_image_8bit()')
        p.terminate()
      except Exception as e:
        logger.exception('Unexpected error: %s', str(e))
      finally:
        elapsed_refresh_time = timer() - start_refresh_time
    else:
      raise Exception('epd_so not defined')

  elapsed_time = timer() - start_time
  logger.info(f'Total time: {round(elapsed_time, 1)} s, refresh: {round(elapsed_refresh_time, 1)} s, API fetch: {round(elapsed_fetch_time, 1)} s, sensor poll: {round(elapsed_sensor_time, 1)}, draw time: {round(elapsed_draw_time, 1)} s')
  logger.info('Refresh complete')
