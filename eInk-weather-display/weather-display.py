#!/usr/bin/python
# -*- coding:utf-8 -*-
import datetime
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.blocking import BlockingScheduler
import log
import logging
import utils
from icons import get_weather_images
import refresh
import ctypes
from typing import Optional
from type_alias import Icons, Fonts
from app_config import AppConfig, ConfigLoadError, load_config
from paths import APP_DIR

CONFIG_FILENAME = APP_DIR / 'config.toml'


class RefreshLoop:
  '''Chooses between full refreshes and updates. A full refresh skipped because the previous run overlapped it is done on the next run.'''

  def __init__(self, panel_size: tuple[int, int], fonts: Fonts, images: Icons, config: AppConfig, epd_so: Optional[ctypes.CDLL]) -> None:
    self.panel_size = panel_size
    self.fonts = fonts
    self.images = images
    self.config = config
    self.epd_so = epd_so
    self.last_full_refresh: Optional[datetime.datetime] = None

  def full_refresh(self) -> None:
    self.last_full_refresh = datetime.datetime.now()
    refresh.refresh(self.panel_size, self.fonts, self.images, self.config, self.epd_so, True)

  def main_loop(self) -> None:
    logger = logging.getLogger(__name__)
    logger.info("main_loop() started")
    wakeup_time = datetime.datetime.now()
    if utils.should_full_refresh(wakeup_time, self.last_full_refresh, self.config.full_refresh_interval):
      self.full_refresh()
    else:
      refresh.refresh(self.panel_size, self.fonts, self.images, self.config, self.epd_so, False)


def main():
  log.setup()
  logger = logging.getLogger(__name__)
  logger.info("App starting")
  try:
    utils.check_python_version()
    utils.check_raqm_support(logger)
    logger.info(f'Reading config file "{CONFIG_FILENAME}"')
    config = load_config(CONFIG_FILENAME)
    logger.info('Config loaded')

    fonts = utils.get_fonts(config)
    images = get_weather_images()
    logger.info(f'Peak memory after startup: {utils.get_peak_memory_mb():.1f} MiB')

    logger.info('Import epd control library')
    (epd_so, panel_size) = utils.get_epd_data(config)

    if config.dev_mode:
      logger.info("Single refresh (dev mode)")
      refresh.refresh(panel_size, fonts, images, config, epd_so, True)
    else:
      logger.info('Starting scheduler')
      # One worker so the initial refresh and the cron job never drive the display at the same time
      scheduler = BlockingScheduler(executors={'default': ThreadPoolExecutor(max_workers=1)})
      refresh_loop = RefreshLoop(panel_size, fonts, images, config, epd_so)
      # Initial full refresh runs as a job so a failure is logged by APScheduler instead of stopping the app
      scheduler.add_job(refresh_loop.full_refresh, next_run_time=datetime.datetime.now())
      # Counted from the start of the hour, so runs land on multiples of the interval (e.g. at :00 seconds for whole minutes).
      # Grace time so a run queued behind a slow refresh (e.g. the initial one) runs late instead of being skipped
      start_of_hour = datetime.datetime.now().replace(minute=0, second=0, microsecond=0)
      scheduler.add_job(refresh_loop.main_loop, 'interval', seconds=config.update_interval, start_date=start_of_hour, misfire_grace_time=30, coalesce=True)
      scheduler.start()

  except KeyboardInterrupt:
    logger.warning("KeyboardInterrupt error")

  except ConfigLoadError as e:
    logger.exception('Config error: %s', str(e))

  except Exception as e:
    logger.exception('Unexpected error: %s', str(e))


if __name__ == "__main__":
  main()
