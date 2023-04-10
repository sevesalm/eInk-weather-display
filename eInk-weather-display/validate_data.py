from jsonschema import validate
from logging import Logger
from typing import Dict, Any


def validate_data(data: Any, schema: Dict, logger: Logger) -> None:
  try:
    validate(data, schema)
  except Exception as e:
    logger.error('Schema validation failed: %s', repr(e))
    raise Exception('Schema validation failed')


observation_data_mapping_schema = {
  'type': 'object',
  'additionalProperties': {
    'type': 'object',
    'required': ['t2m', 'rh', 'p_sea', 'ws_10min', 'wd_10min', 'wg_10min', 'n_man', 'wawa'],
    'additionalProperties': False,
    'properties': {
      't2m': {
        'type': 'number'
      },
      'rh': {
        'type': 'number'
      },
      'p_sea': {
        'type': 'number'
      },
      'ws_10min': {
        'type': 'number'
      },
      'wd_10min': {
        'type': 'number'
      },
      'wg_10min': {
        'type': 'number'
      },
      'n_man': {
        'type': 'integer'
      },
      'wawa': {
        'type': 'integer'
      }
    }
  }
}

radiation_data_mapping_schema = {
  'type': 'object',
  'additionalProperties': {
    'type': 'object',
    'required': ['dir_1min'],
    'additionalProperties': False,
    'properties': {
      'dir_1min': {
        'type': 'number'
      }
    }
  }
}

forecast_data_mapping_schema = {
  'type': 'object',
  'additionalProperties': {
    'type': 'object',
    'required': ['Temperature', 'WindSpeedMS', 'WindDirection', 'TotalCloudCover', 'WeatherSymbol3'],
    'additionalProperties': False,
    'properties': {
      'Temperature': {
        'type': 'number'
      },
      'WindSpeedMS': {
        'type': 'number'
      },
      'WindDirection': {
        'type': 'number'
      },
      'TotalCloudCover': {
        'type': 'number'
      },
      'WeatherSymbol3': {
        'type': 'integer'
      },
    }
  }
}
