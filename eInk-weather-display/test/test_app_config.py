import unittest
from pathlib import Path
from tempfile import NamedTemporaryFile

from app_config import ConfigLoadError, load_config


VALID_CONFIG = """
[general]
dev_mode = true
dev_mode_output_filename = "image.png"

dev_mode_random_weather_data = false
dev_mode_random_sensor_data = true

log_sensor_data = false
sensor_data_log_filename = "battery.log"

fmi_location = "Helsinki"
fmi_observation_location_override = "Espoo"

override_name = "Home"
override_latitude = 60.1699
override_longitude = 24.9384

draw_panel_borders = false
draw_borders = true

ruuvitag_mac_out = "AA:BB:CC:DD:EE:FF"
ruuvitag_mac_out_name = "Out"

sensor_poll_timeout = 10

rotate_180 = true
mirror_horizontal = false

epd_model = "10.3"
epd_voltage = 1140
bits_per_pixel = 4

refresh_full_interval = 60
refresh_partial_interval = 1

high_temperature_warning_threshold = 25
extreme_high_temperature_warning_threshold = 30
low_temperature_warning_threshold = -20
extreme_low_temperature_warning_threshold = -30
tropical_night_temperature_warning_threshold = 20
"""


class TestAppConfig(unittest.TestCase):
  def _write_temp_config(self, content: str) -> Path:
    temp_file = NamedTemporaryFile(mode='w', suffix='.ini', delete=False)
    with temp_file as handle:
      handle.write(content)
    return Path(temp_file.name)

  def test_load_config_success(self):
    config_file = self._write_temp_config(VALID_CONFIG)
    config = load_config(str(config_file))
    self.assertTrue(config.dev_mode)
    self.assertEqual(config.epd_model, '10.3')
    self.assertEqual(config.bits_per_pixel, 4)

  def test_unknown_key_fails(self):
    config_file = self._write_temp_config(VALID_CONFIG + "\nunknown_key = 123\n")
    with self.assertRaises(ConfigLoadError):
      load_config(str(config_file))

  def test_invalid_extreme_temperature_threshold_order_fails(self):
    invalid = VALID_CONFIG.replace(
      "high_temperature_warning_threshold = 25",
      "high_temperature_warning_threshold = 35",
    )
    config_file = self._write_temp_config(invalid)
    with self.assertRaises(ConfigLoadError):
      load_config(str(config_file))

  def test_invalid_temperature_threshold_order_fails(self):
    invalid = VALID_CONFIG.replace(
      "high_temperature_warning_threshold = 25",
      "high_temperature_warning_threshold = -25",
    )
    config_file = self._write_temp_config(invalid)
    with self.assertRaises(ConfigLoadError):
      load_config(str(config_file))


if __name__ == '__main__':
  unittest.main()
