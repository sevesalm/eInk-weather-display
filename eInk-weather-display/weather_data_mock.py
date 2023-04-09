from datetime import datetime, timedelta
import random
from zoneinfo import ZoneInfo
from logging import Logger
from typing import Mapping, List, Tuple
from type_alias import ApiData, WeatherData
from icon_mapping import observation_mapping, forecast_mapping
import utils


def get_random_coordinates() -> Tuple[str, str]:
  return (str(random.uniform(-90, 90)), str(random.uniform(-180, 180)))


def get_random_observation_data(logger: Logger) -> WeatherData:
  ws_10min = random.uniform(0, 20)
  now = datetime.today().isoformat()
  observation_data: ApiData = {now: {
    't2m': random.uniform(-30, 40),
    'rh': random.uniform(10, 90),
    'p_sea': random.uniform(900, 1100),
    'ws_10min': ws_10min,
    'wd_10min': random.uniform(0, 360),
    'wg_10min': ws_10min + random.uniform(0, 10),
    'n_man': random.randint(0, 8),
    'wawa': random.choice(list(observation_mapping.keys()))
  }}
  position = get_random_coordinates()
  result: WeatherData = (observation_data, position, 'Helsinki', '12345')
  logger.info('Using random observation data: %s', repr(result))
  return result


def get_random_radiation_data(logger: Logger) -> ApiData:
  start_date = datetime.today()
  now = start_date.astimezone(tz=ZoneInfo('UTC')).isoformat()
  now = datetime.today().isoformat()
  radiation_data: ApiData = {now: {
    'dir_1min': random.uniform(0, 200)
  }}
  logger.info('Using random radiation data: %s', repr(radiation_data))
  return radiation_data


def get_random_forecast_data(logger: Logger) -> WeatherData:
  start_date = utils.get_next_forecast_start_timestamp()
  forecast_datetimes: List[str] = []
  for i in range(7):
    new_datetime = start_date + i*timedelta(hours=6)
    forecast_datetimes.append(new_datetime.astimezone(tz=ZoneInfo('UTC')).isoformat())
  forecast_data = {}
  for forecast_datetime in forecast_datetimes:
    data: Mapping[str, float] = {
      'Temperature': random.uniform(-30, 40),
      'WindSpeedMS': random.uniform(0, 20),
      'WindDirection': random.uniform(0, 360),
      'TotalCloudCover': random.uniform(0, 100),
      'WeatherSymbol3': random.choice(list(forecast_mapping.keys()))
    }
    forecast_data[forecast_datetime] = data
  position = get_random_coordinates()
  result: WeatherData = (forecast_data, position, 'Helsinki', '12345')
  logger.info('Using random forecast data: %s', repr(result))
  return result
