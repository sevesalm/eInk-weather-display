import xml.etree.ElementTree as et
from datetime import datetime
import requests
from configparser import SectionProxy
from zoneinfo import ZoneInfo
from itertools import zip_longest
from logging import Logger
from typing import Optional, Dict, List
from type_alias import ObservationData, ForecastData, RadiationData
from weather_data_mock import get_random_forecast_data, get_random_observation_data, get_random_radiation_data
import utils
from validate_data import validate_data, observation_data_mapping_schema, radiation_data_mapping_schema, forecast_data_mapping_schema

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
  response.raise_for_status()
  return et.fromstring(response.content)


def parse_multipoint_data(xml_data: et.Element, count: int, skip_count: Optional[int] = 1, reversed: bool = False) -> Dict:
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
  if (element is None or element.text is None):
    raise Exception('Could not find any position data')
  position_data = element.text.split(' ')[:-1]
  if (len(position_data) != 2):
    raise Exception('Could not parse position data')
  return (position_data[0], position_data[1])


# TODO: Can return None also
def get_fmisid(xml_data: et.Element) -> str:
  ns = {'gml': 'http://www.opengis.net/gml/3.2'}
  element = xml_data.find('.//gml:identifier', ns)
  if (element is None or element.text is None):
    raise Exception('Could not find any fmisid data')
  return element.text


# TODO: Can return None also
def get_position_name(xml_data: et.Element) -> str:
  ns = {'gml': 'http://www.opengis.net/gml/3.2'}
  element = xml_data.find('.//gml:name', ns)
  if (element is None or element.text is None):
    raise Exception('Could not find any position name data')
  return element.text


def get_radiation_data(config: SectionProxy, observation_data: Optional[ObservationData], logger: Logger) -> Optional[RadiationData]:
  if (observation_data is None):
    return None
  try:
    if (config.getboolean('DEV_MODE_RANDOM_WEATHER_DATA') and config.getboolean('DEV_MODE')):
      return get_random_radiation_data(logger)
    params = {
      'fmisid': observation_data[3],
      'parameters': ','.join(RADIATION_PARAMETERS)
    }
    xml_data = fetch_data(RADIATION_QUERY, params)
    radiation_data = parse_multipoint_data(xml_data, 1)
    validate_data(radiation_data, radiation_data_mapping_schema, logger)
    logger.info('Received radiation data: %s', repr(radiation_data))
    return radiation_data
  except Exception as e:
    logger.error('Error fetching radiation data:  %s', repr(e))
    return None


def get_observation_data(config: SectionProxy, logger: Logger) -> Optional[ObservationData]:
  try:
    if (config.getboolean('DEV_MODE_RANDOM_WEATHER_DATA') and config.getboolean('DEV_MODE')):
      return get_random_observation_data(logger)
    params = {
      'place': config['FMI_LOCATION'],
      'parameters': ','.join(OBS_PARAMETERS)
    }
    xml_data = fetch_data(OBS_QUERY, params)
    observation_data = parse_multipoint_data(xml_data, 1)
    validate_data(observation_data, observation_data_mapping_schema, logger)
    position = get_position(xml_data)
    position_name = get_position_name(xml_data)
    fmisid = get_fmisid(xml_data)
    result = (observation_data, position, position_name, fmisid)
    logger.info('Received observation data: %s', repr(result))
    return result
  except Exception as e:
    logger.error('Error while fetching observation data: %s', repr(e))
    return None


def get_forecast_data(config: SectionProxy, count: int, skip_count: Optional[int], logger: Logger) -> Optional[ForecastData]:
  try:
    if (config.getboolean('DEV_MODE_RANDOM_WEATHER_DATA') and config.getboolean('DEV_MODE')):
      return get_random_forecast_data(logger)
    params = {
      'place': config['FMI_LOCATION'],
      'parameters': ','.join(FORECAST_PARAMETERS),
      'starttime': utils.get_next_forecast_start_timestamp().isoformat()
    }
    xml_data = fetch_data(FORECAST_QUERY, params)
    forecast_data = parse_multipoint_data(xml_data, count, skip_count, True)
    validate_data(forecast_data, forecast_data_mapping_schema, logger)
    position = get_position(xml_data)
    position_name = get_position_name(xml_data)
    fmisid = get_fmisid(xml_data)
    result = (forecast_data, position, position_name, fmisid)
    logger.info('Received forecast data: %s', repr(result))
    return result
  except Exception as e:
    logger.error('Error while fetching forecast data: %s', repr(e))
    return None
