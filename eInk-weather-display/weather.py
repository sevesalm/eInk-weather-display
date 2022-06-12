import xml.etree.ElementTree as et
from datetime import datetime, timedelta
import requests
import random
from configparser import SectionProxy
from zoneinfo import ZoneInfo
from itertools import zip_longest
from logging import Logger
from typing import Mapping, Optional, Dict, List, Tuple
from type_alias import ApiData, WeatherData, Datetime
from icon_mapping import observation_mapping, forecast_mapping

FMI_API_URL = 'http://opendata.fmi.fi/wfs/eng'
OBS_PARAMETERS = ['t2m', 'rh', 'p_sea', 'ws_10min', 'wd_10min', 'wg_10min', 'n_man', 'wawa']
OBS_QUERY = 'fmi::observations::weather::multipointcoverage'
FORECAST_PARAMETERS = ['Temperature', 'WindSpeedMS', 'WindDirection', 'TotalCloudCover', 'WeatherSymbol3']
FORECAST_QUERY = 'fmi::forecast::harmonie::surface::point::multipointcoverage'
RADIATION_QUERY = 'fmi::observations::radiation::multipointcoverage'
RADIATION_PARAMETERS = ['dir_1min']


def split_in_chunks(data: List, size: int):
    if (len(data) % size != 0):
      raise Exception('Bad multicoverage data')
    args = [iter(data)] * size
    return zip_longest(*args)


def fetch_data(query_type: str, extra_params: Dict[str, str] = {}) -> et.Element:
  base_params = {
    'service': 'WFS',
    'version': '2.0.0',
    'request': 'GetFeature',
    'storedQuery_id': query_type,
    }

  params = base_params | extra_params

  response = requests.get(FMI_API_URL, params=params)
  return et.fromstring(response.content)


def parse_multipoint_data(xml_data: et.Element, count: int, skip_count: Optional[int] = 1, reversed: bool = False) -> ApiData:
  ns = {'gml': 'http://www.opengis.net/gml/3.2', 'gmlcov': 'http://www.opengis.net/gmlcov/1.0', 'swe': 'http://www.opengis.net/swe/2.0'}
  parameter_element = xml_data.find('.//swe:DataRecord', ns)
  pos_element = xml_data.find('.//gmlcov:positions', ns)
  data_element = xml_data.find('.//gml:doubleOrNilReasonTupleList', ns)
  result = {}
  if parameter_element is not None and pos_element is not None and pos_element.text is not None and data_element is not None and data_element.text is not None:
    params = [row.attrib["name"] for row in parameter_element]
    positions = pos_element.text.strip().split('\n')
    times = [datetime.fromtimestamp(int(row.split()[2]), ZoneInfo('UTC')) for row in positions]
    datas = data_element.text.strip().split()
    data_chunks = list(split_in_chunks(datas, len(params)))
    if not reversed:
      time_data = list(zip(times, data_chunks))[::skip_count][-count:]
    else:
      time_data = list(zip(times, data_chunks))[::skip_count][:count]
    for time, data_tuple in time_data:
      param_data = zip(params, data_tuple)
      data = {param: float(data) for param, data in param_data}
      result[time.isoformat()] = data
  return result


def get_position(xml_data: et.Element) -> tuple[str, str]:
  ns = {'gml': 'http://www.opengis.net/gml/3.2'}
  element = xml_data.find('.//gml:pos', ns)
  if(element is None or element.text is None):
    raise Exception('Could not find any position data')
  position_data = element.text.split(' ')[:-1]
  return (position_data[0], position_data[1])


def get_fmisid(xml_data: et.Element) -> str:
  ns = {'gml': 'http://www.opengis.net/gml/3.2'}
  element = xml_data.find('.//gml:identifier', ns)
  if(element is None or element.text is None):
    raise Exception('Could not find any fmisid data')
  return element.text


def get_position_name(xml_data: et.Element) -> str:
  ns = {'gml': 'http://www.opengis.net/gml/3.2'}
  element = xml_data.find('.//gml:name', ns)
  if(element is None or element.text is None):
    raise Exception('Could not find any position name data')
  return element.text


def combine(data_sets: list[ApiData]) -> ApiData:
  data = {}
  for data_set in data_sets:
    for key, val in data_set.items():
      if(key not in data):
        data[key] = val
      else:
        data[key].update(val)
  return data


def get_next_forecast_start_timestamp() -> Datetime:
  now = datetime.today()
  new_hour = ((now.hour-3)//6 + 1) * 6 + 3
  new_time = (now + timedelta(hours=new_hour - now.hour)).replace(minute=0, second=0, microsecond=0).astimezone(tz=None)
  return new_time


def get_radiation_data(fmisid: str, logger: Logger) -> ApiData:
  params = {
    'fmisid': fmisid,
    'parameters': ','.join(RADIATION_PARAMETERS)
  }
  xml_data = fetch_data(RADIATION_QUERY, params)
  radiation_data = parse_multipoint_data(xml_data, 1)
  result = (radiation_data)
  logger.info('Received radiation data: %s', repr(result))
  return result


def get_observation_data(config: SectionProxy, logger: Logger) -> WeatherData:
  if (config.getboolean('USE_RANDOM_DATA')):
    return get_random_observation_data(logger)
  params = {
    'place': config['FMI_LOCATION'],
    'parameters': ','.join(OBS_PARAMETERS)
  }
  xml_data = fetch_data(OBS_QUERY, params)
  observation_data = parse_multipoint_data(xml_data, 1)
  position = get_position(xml_data)
  position_name = get_position_name(xml_data)
  fmisid = get_fmisid(xml_data)
  result = (observation_data, position, position_name, fmisid)
  logger.info('Received observation data: %s', repr(result))
  return result


def get_forecast_data(config: SectionProxy, count: int, skip_count: Optional[int], logger: Logger) -> WeatherData:
  if (config.getboolean('USE_RANDOM_DATA')):
    return get_random_forecast_data(logger)
  params = {
    'place': config['FMI_LOCATION'],
    'parameters': ','.join(FORECAST_PARAMETERS),
    'starttime': get_next_forecast_start_timestamp().isoformat()
  }
  xml_data = fetch_data(FORECAST_QUERY, params)
  forecast_data = parse_multipoint_data(xml_data, count, skip_count, True)
  position = get_position(xml_data)
  position_name = get_position_name(xml_data)
  fmisid = get_fmisid(xml_data)
  result = (forecast_data, position, position_name, fmisid)
  logger.info('Received forecast data: %s', repr(result))
  return result


def get_random_coordinates() -> Tuple[str, str]:
  return (str(random.uniform(-90, 90)), str(random.uniform(-180, 180)))


def get_random_observation_data(logger: Logger) -> WeatherData:
  ws_10min = random.uniform(0, 20)
  observation_data: ApiData = {'2022-01-01T13:00:00Z': {
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


def get_random_forecast_data(logger: Logger) -> WeatherData:
  start_date = get_next_forecast_start_timestamp()
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
