import xml.etree.ElementTree as et
import io 
import pytz
from datetime import datetime, timedelta
import requests

OBS_PARAMETERS=['t2m', 'rh', 'p_sea', 'ws_10min', 'wd_10min', 'wawa']
OBS_ID='fmi::observations::weather::timevaluepair'
OBS_TIMESTEP = 60
FORECAST_PARAMETERS=['Temperature', 'WindSpeedMS', 'WindDirection', 'WeatherSymbol3']
FORECAST_ID='fmi::forecast::harmonie::surface::point::timevaluepair'
FORECAST_TIMESTEP=360
MEASUREMENTS=3
FMI_API_URL = 'http://opendata.fmi.fi/wfs/eng'

def fetch_data(query_type, place, parameters, start_time = None):
  params = {
    'service': 'WFS',
    'version': '2.0.0',
    'request': 'GetFeature',
    'storedQuery_id': query_type,
    'place': place,
    'parameters': ','.join(parameters),
    'starttime': start_time
    }
  response = requests.get(FMI_API_URL, params=params)
  return et.fromstring(response.content)

def parse_data(xml_data, parameter, prefix, count, reversed, skip_count = 1):
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
      prefix, has_namespace, postfix = child.tag.partition('}')
      el_data[postfix] = child.text
    data[el_data['time']] =  {parameter: float(el_data['value'])}
  return data

def get_first_position(xml_data):
  ns = {'gml': 'http://www.opengis.net/gml/3.2'}
  elements = xml_data.findall('.//gml:pos', ns)
  if(len(elements) == 0):
    raise Exception('Could not find any position data') 
  position_data = elements[0].text.split(' ')[:-1]
  return (position_data[0], position_data[1])

def combine(data_sets):
  data = {}
  for data_set in data_sets:
    for key, val in data_set.items():
      if(not key in data):
        data[key] = val
      else:
        data[key].update(val)
  return data

def get_observations(place, count):
  xml_data = fetch_data(OBS_ID, place, OBS_PARAMETERS)
  observation_data = combine([parse_data(xml_data, parameter, 'obs-obs-1-1-', count, False) for parameter in OBS_PARAMETERS])
  first_position = get_first_position(xml_data)
  return (observation_data, first_position)

def get_next_forecast_start_timestamp():
  now = datetime.today()
  new_hour = ((now.hour-3)//6 + 1) * 6 + 3
  new_time = (now + timedelta(hours=new_hour - now.hour)).replace(minute=0, second=0, microsecond=0).astimezone(tz=None).isoformat()
  return new_time

def get_forecasts(place, count, skip_count, next_timestamp = None):
  if (next_timestamp == None):
    next_timestamp = get_next_forecast_start_timestamp()
  xml_data = fetch_data(FORECAST_ID, place, FORECAST_PARAMETERS, next_timestamp)
  forecast_data = combine([parse_data(xml_data, parameter, 'mts-1-1-', count, True, skip_count) for parameter in FORECAST_PARAMETERS])
  first_position = get_first_position(xml_data)
  return (forecast_data, first_position)

