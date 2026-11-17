import logging
import math
import unittest
from validate_data import validate_data, observation_data_mapping_schema, forecast_data_mapping_schema

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
logger.propagate = False


class TestValidateData(unittest.TestCase):
  def test_forecast_nan_symbols(self):
    data = {
      '2026-11-17T12:00:00+00:00': {
        'Temperature': 1.0,
        'WindSpeedMS': 2.0,
        'WindDirection': 180.0,
        'TotalCloudCover': 50.0,
        'WeatherSymbol3': math.nan,
        'SmartSymbol': math.nan,
      }
    }
    validate_data(data, forecast_data_mapping_schema, logger)

  def test_forecast_missing_symbol(self):
    data = {
      '2026-11-17T12:00:00+00:00': {
        'Temperature': 1.0,
        'WindSpeedMS': 2.0,
        'WindDirection': 180.0,
        'TotalCloudCover': 50.0,
        'WeatherSymbol3': 1.0,
      }
    }
    with self.assertRaises(Exception):
      validate_data(data, forecast_data_mapping_schema, logger)

  def test_observation_nan_wawa(self):
    data = {
      '2026-11-17T12:00:00+00:00': {
        't2m': 1.0,
        'rh': 80.0,
        'p_sea': 1013.0,
        'ws_10min': 2.0,
        'wd_10min': 180.0,
        'wg_10min': 3.0,
        'n_man': 8.0,
        'wawa': math.nan,
      }
    }
    validate_data(data, observation_data_mapping_schema, logger)


if __name__ == '__main__':
    unittest.main()
