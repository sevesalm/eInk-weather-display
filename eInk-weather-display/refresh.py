import ctypes
import logging
import time
from PIL import Image, ImageDraw
from utils import get_config_override_position, get_peak_memory_mb
from observation_panel import get_observation_panel
from info_panel import get_info_panel
from forecast_panel import get_forecasts_panel
from celestial_panel import get_celestial_panel
from sensor_panel import get_sensor_panel
from timeit import default_timer as timer
from typing import Optional
from type_alias import Icons, Fonts
from weather_data import get_observation_data, get_forecast_data, get_radiation_data
from app_config import AppConfig
from sensor_data import get_sensor_data


def refresh(panel_size: tuple[int, int], fonts: Fonts, images: Icons, config: AppConfig, epd_so: Optional[ctypes.CDLL], init: bool) -> None:
  logger = logging.getLogger(__name__)
  logger.info('Refresh started')
  start_time = timer()
  start_cpu_time = time.process_time()

  # Fetch data
  start_fetch_time = timer()
  observation_data = get_observation_data(config, logger)
  elapsed_observation_time = timer() - start_fetch_time
  start_radiation_time = timer()
  radiation_data = get_radiation_data(config, observation_data, logger)
  elapsed_radiation_time = timer() - start_radiation_time
  start_forecast_time = timer()
  forecast_data = get_forecast_data(config, 7, 6, logger)
  elapsed_forecast_time = timer() - start_forecast_time
  elapsed_fetch_time = timer() - start_fetch_time

  start_sensor_time = timer()
  sensor_data = get_sensor_data(config, logger)

  elapsed_sensor_time = timer() - start_sensor_time

  # Draw individual panels
  logger.info('Drawing panels')
  start_draw_time = timer()
  observation_panel = get_observation_panel(observation_data, radiation_data, images, fonts, config)
  sensor_panel = get_sensor_panel(sensor_data, fonts, config)
  forecasts_panel = get_forecasts_panel(forecast_data, images, fonts, config)
  (_, position, position_name, _) = forecast_data if forecast_data is not None else (None, get_config_override_position(config), config.override_name, None)
  celestial_panel = get_celestial_panel(position, position_name, fonts, images, config)
  info_panel = get_info_panel(fonts, config)

  # Paste the panels on the main image
  logger.info('Pasting panels')
  full_image = Image.new('L', (panel_size[0], panel_size[1]), 0xff)
  full_image.paste(observation_panel, (0, 0))
  full_image.paste(sensor_panel, (observation_panel.width, 0))
  full_image.paste(forecasts_panel, (0, panel_size[1] - forecasts_panel.height))
  full_image.paste(celestial_panel, (observation_panel.width + sensor_panel.width, 0))
  full_image.paste(info_panel, (panel_size[0] - info_panel.width, 0))
  elapsed_draw_time = timer() - start_draw_time

  if (config.draw_borders):
    border_color = 0x80
    draw_width = 2
    draw = ImageDraw.Draw(full_image)
    draw.line([0, panel_size[1] - forecasts_panel.height, panel_size[0], panel_size[1] - forecasts_panel.height], fill=border_color, width=draw_width)
    draw.line([observation_panel.width, 0, observation_panel.width, observation_panel.height - panel_size[1]//20], fill=border_color, width=draw_width)
    draw.line([observation_panel.width + sensor_panel.width, 0, observation_panel.width + sensor_panel.width, observation_panel.height - panel_size[1]//20], fill=border_color, width=draw_width)
    draw.line([observation_panel.width + sensor_panel.width + celestial_panel.width, 0, observation_panel.width + sensor_panel.width + celestial_panel.width, observation_panel.height - panel_size[1]//20], fill=border_color, width=draw_width)

  if (config.dev_mode):
    filename = config.dev_mode_output_filename
    logger.info(f'Saving image to {filename}')
    full_image.save(filename)
    elapsed_refresh_time = 0
    elapsed_transform_time = 0
  else:
    logger.info(f'Sending image to EPD, {"full" if init else "partial"} refresh')
    start_transform_time = timer()
    if (config.mirror_horizontal):
      full_image = full_image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    image_bytes = full_image.rotate(0 if not config.rotate_180 else 180, expand=True).tobytes()
    elapsed_transform_time = timer() - start_transform_time
    c_logger = ctypes.CFUNCTYPE(None, ctypes.c_int, ctypes.c_wchar_p)(logging.getLogger('esp.so').log)
    if (epd_so):
      start_refresh_time = timer()
      try:
        # The C library times out on its own if the controller stops responding
        return_code = epd_so.draw_image_8bit(image_bytes, ctypes.c_bool(init), ctypes.c_int(config.epd_voltage), config.bits_per_pixel, c_logger)
        logger.debug(f'Return code: {return_code}')
        if (return_code != 0):
          logger.error(f'draw_image_8bit() failed with return code {return_code}')
      except Exception as e:
        logger.exception('Unexpected error: %s', str(e))
      finally:
        elapsed_refresh_time = timer() - start_refresh_time
    else:
      raise Exception('epd_so not defined')

  elapsed_time = timer() - start_time
  # Includes CPU time spent inside the C library, which runs in this process
  elapsed_cpu_time = time.process_time() - start_cpu_time
  logger.info(f'Total time: {elapsed_time:.2f} s, CPU time: {elapsed_cpu_time:.2f} s, refresh: {elapsed_refresh_time:.2f} s, '
              f'API fetch: {elapsed_fetch_time:.2f} s (observation: {elapsed_observation_time:.2f} s, radiation: {elapsed_radiation_time:.2f} s, forecast: {elapsed_forecast_time:.2f} s), '
              f'sensor poll: {elapsed_sensor_time:.2f} s, draw time: {elapsed_draw_time:.2f} s, image transform: {elapsed_transform_time:.2f} s, peak memory: {get_peak_memory_mb():.1f} MiB')
  logger.info('Refresh complete')
