import xml.etree.ElementTree as et
from datetime import datetime, timedelta
import requests
from logging import Logger
from typing import Optional, Dict, List
from type_alias import ApiData, WeatherData
from itertools import zip_longest
from zoneinfo import ZoneInfo

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


def get_next_forecast_start_timestamp() -> str:
  now = datetime.today()
  new_hour = ((now.hour-3)//6 + 1) * 6 + 3
  new_time = (now + timedelta(hours=new_hour - now.hour)).replace(minute=0, second=0, microsecond=0).astimezone(tz=None).isoformat()
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


def get_observation_data(place: str, logger: Logger) -> WeatherData:
  params = {
    'place': place,
    'parameters': ','.join(OBS_PARAMETERS)
  }
  xml_data = fetch_data(OBS_QUERY, params)
  observation_data = parse_multipoint_data(xml_data, 1)
  position = get_position(xml_data)
  position_name = get_position_name(xml_data)
  result = (observation_data, position, position_name)
  logger.info('Received observation data: %s', repr(result))
  return result


def get_forecast_data(place: str, count: int, skip_count: Optional[int], logger: Logger) -> WeatherData:
  params = {
    'place': place,
    'parameters': ','.join(FORECAST_PARAMETERS),
    'starttime': get_next_forecast_start_timestamp()
  }
  xml_data = fetch_data(FORECAST_QUERY, params)
  forecast_data = parse_multipoint_data(xml_data, count, skip_count, True)
  position = get_position(xml_data)
  position_name = get_position_name(xml_data)
  result = (forecast_data, position, position_name)
  logger.info('Received forecast data: %s', repr(result))
  return result
