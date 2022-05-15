import xml.etree.ElementTree as et
from datetime import datetime, timedelta
import requests
from logging import Logger
from typing import Optional
from type_alias import ApiData, WeatherData

OBS_PARAMETERS = ['t2m', 'rh', 'p_sea', 'ws_10min', 'wd_10min', 'wg_10min', 'n_man', 'wawa']
# OBS_PARAMETERS=['t2m', 'rh', 'p_sea', 'ws_10min', 'wd_10min', 'wg_10min','n_man', 'dir_1min', 'wawa']
OBS_ID = 'fmi::observations::weather::timevaluepair'
FORECAST_PARAMETERS = ['Temperature', 'WindSpeedMS', 'WindDirection', 'TotalCloudCover', 'WeatherSymbol3']
FORECAST_ID = 'fmi::forecast::harmonie::surface::point::timevaluepair'
FMI_API_URL = 'http://opendata.fmi.fi/wfs/eng'


def fetch_data(query_type: str, place: str, parameters: list[str], start_time: Optional[str] = None, timestep: Optional[str] = None) -> et.Element:
  params = {
    'service': 'WFS',
    'version': '2.0.0',
    'request': 'GetFeature',
    'storedQuery_id': query_type,
    'place': place,
    'parameters': ','.join(parameters),
    'starttime': start_time,
    'timestep': timestep
    }
  response = requests.get(FMI_API_URL, params=params)
  return et.fromstring(response.content)


def parse_data(xml_data: et.Element, parameter: str, prefix: str, count: int, reversed: bool, skip_count: Optional[int] = 1) -> ApiData:
  ns = {'wml2': 'http://www.opengis.net/waterml/2.0', 'gml32': 'http://www.opengis.net/gml/3.2'}
  elements = xml_data.findall(f'.//wml2:MeasurementTimeseries[@gml32:id="{prefix}{parameter}"]//wml2:MeasurementTVP', ns)
  data = {}
  if(reversed):
    wanted_elements = elements[::skip_count][:count]
  else:
    wanted_elements = elements[::skip_count][-count:]
  for el in wanted_elements:
    el_data = {}
    for child in el:
      _, _, postfix = child.tag.partition('}')
      el_data[postfix] = child.text
    data[el_data['time']] = {parameter: float(el_data['value'])}
  return data


def get_position(xml_data) -> tuple[str, str]:
  ns = {'gml': 'http://www.opengis.net/gml/3.2'}
  elements = xml_data.findall('.//gml:pos', ns)
  if(len(elements) == 0):
    raise Exception('Could not find any position data')
  position_data = elements[0].text.split(' ')[:-1]
  return (position_data[0], position_data[1])


def get_position_name(xml_data: et.Element) -> str:
  ns = {'gml': 'http://www.opengis.net/gml/3.2'}
  elements = xml_data.findall('.//gml:name', ns)
  if(len(elements) == 0 or elements[0].text is None):
    raise Exception('Could not find any position name data')
  return elements[0].text


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


def get_observation_data(place: str, logger: Logger) -> WeatherData:
  xml_data = fetch_data(OBS_ID, place, OBS_PARAMETERS, None, None)
  # xml_data = fetch_data(OBS_ID, place, OBS_PARAMETERS, None, 10)
  observation_data = combine([parse_data(xml_data, parameter, 'obs-obs-1-1-', 1, False) for parameter in OBS_PARAMETERS])
  position = get_position(xml_data)
  position_name = get_position_name(xml_data)
  result = (observation_data, position, position_name)
  logger.info('Received observation data: %s', repr(result))
  return result


def get_forecast_data(place: str, count: int, skip_count: Optional[int], logger: Logger, next_timestamp: Optional[str] = None) -> WeatherData:
  if (next_timestamp is None):
    next_timestamp = get_next_forecast_start_timestamp()
  xml_data = fetch_data(FORECAST_ID, place, FORECAST_PARAMETERS, next_timestamp)
  forecast_data = combine([parse_data(xml_data, parameter, 'mts-1-1-', count, True, skip_count) for parameter in FORECAST_PARAMETERS])
  position = get_position(xml_data)
  position_name = get_position_name(xml_data)
  result = (forecast_data, position, position_name)
  logger.info('Received forecast data: %s', repr(result))
  return result
