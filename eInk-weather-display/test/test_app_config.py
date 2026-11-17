import unittest
from pathlib import Path
from tempfile import NamedTemporaryFile

from app_config import ConfigLoadError, HomeAssistantSensor, RuuviSensor, load_config


VALID_CONFIG = """
dev_mode = true
dev_mode_output_filename = "image.png"

dev_mode_random_weather_data = false
dev_mode_random_sensor_data = true

fmi_location = "Helsinki"
fmi_observation_location_override = "Espoo"

override_name = "Home"
override_latitude = 60.1699
override_longitude = 24.9384

draw_panel_borders = false
draw_borders = true

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

SENSORS_CONFIG = """
[home_assistant]
url = "http://homeassistant.local:8123"
bearer_token = "token"

[[sensors]]
type = "Ruuvi"
name = "Out"
mac = "AA:BB:CC:DD:EE:FF"

[[sensors]]
type = "HomeAssistant"
name = "Living room"
temperature_sensor_id = "sensor.living_room_temperature"
humidity_sensor_id = "sensor.living_room_humidity"
"""


class TestAppConfig(unittest.TestCase):
  def _write_temp_config(self, content: str) -> Path:
    temp_file = NamedTemporaryFile(mode='w', suffix='.toml', delete=False)
    with temp_file as handle:
      handle.write(content)
    path = Path(temp_file.name)
    self.addCleanup(path.unlink, missing_ok=True)
    return path

  def test_load_config_success(self):
    config_file = self._write_temp_config(VALID_CONFIG)
    config = load_config(str(config_file))
    self.assertTrue(config.dev_mode)
    self.assertEqual(config.epd_model, '10.3')
    self.assertEqual(config.bits_per_pixel, 4)

  def test_unknown_key_fails(self):
    config_file = self._write_temp_config(VALID_CONFIG + "\nunknown_key = 123\n")
    with self.assertRaisesRegex(ConfigLoadError, r'unknown_key\s+Extra inputs are not permitted'):
      load_config(str(config_file))

  def test_invalid_extreme_temperature_threshold_order_fails(self):
    invalid = VALID_CONFIG.replace(
      "high_temperature_warning_threshold = 25",
      "high_temperature_warning_threshold = 35",
    )
    config_file = self._write_temp_config(invalid)
    with self.assertRaisesRegex(ConfigLoadError, 'extreme_high_temperature_warning_threshold must be >='):
      load_config(str(config_file))

  def test_invalid_temperature_threshold_order_fails(self):
    invalid = VALID_CONFIG.replace(
      "high_temperature_warning_threshold = 25",
      "high_temperature_warning_threshold = -25",
    )
    config_file = self._write_temp_config(invalid)
    with self.assertRaisesRegex(ConfigLoadError, 'low_temperature_warning_threshold must be <='):
      load_config(str(config_file))

  def test_invalid_tropical_night_threshold_fails(self):
    invalid = VALID_CONFIG.replace(
      "tropical_night_temperature_warning_threshold = 20",
      "tropical_night_temperature_warning_threshold = 26",
    )
    config_file = self._write_temp_config(invalid)
    with self.assertRaisesRegex(ConfigLoadError, 'tropical_night_temperature_warning_threshold must be'):
      load_config(str(config_file))

  def test_empty_string_fails(self):
    invalid = VALID_CONFIG.replace('fmi_location = "Helsinki"', 'fmi_location = "  "')
    config_file = self._write_temp_config(invalid)
    with self.assertRaisesRegex(ConfigLoadError, r'fmi_location\s+String should have at least 1 character'):
      load_config(str(config_file))

  def test_latitude_out_of_range_fails(self):
    invalid = VALID_CONFIG.replace('override_latitude = 60.1699', 'override_latitude = 91')
    config_file = self._write_temp_config(invalid)
    with self.assertRaisesRegex(ConfigLoadError, r'override_latitude\s+Input should be less than or equal to 90'):
      load_config(str(config_file))

  def test_zero_sensor_poll_timeout_fails(self):
    invalid = VALID_CONFIG.replace('sensor_poll_timeout = 10', 'sensor_poll_timeout = 0')
    config_file = self._write_temp_config(invalid)
    with self.assertRaisesRegex(ConfigLoadError, r'sensor_poll_timeout\s+Input should be greater than 0'):
      load_config(str(config_file))

  def test_refresh_interval_over_60_fails(self):
    invalid = VALID_CONFIG.replace('refresh_full_interval = 60', 'refresh_full_interval = 120')
    config_file = self._write_temp_config(invalid)
    with self.assertRaisesRegex(ConfigLoadError, r'refresh_full_interval\s+Input should be less than or equal to 60'):
      load_config(str(config_file))

  def test_duplicate_sensor_names_fail(self):
    duplicate = SENSORS_CONFIG.replace('name = "Living room"', 'name = "Out"')
    config_file = self._write_temp_config(VALID_CONFIG + duplicate)
    with self.assertRaisesRegex(ConfigLoadError, 'Sensor names must be unique, duplicates: Out'):
      load_config(str(config_file))

  def test_sensors_parsed_by_type(self):
    config_file = self._write_temp_config(VALID_CONFIG + SENSORS_CONFIG)
    config = load_config(str(config_file))
    self.assertEqual(len(config.sensors), 2)
    (ruuvi, home_assistant) = config.sensors
    assert isinstance(ruuvi, RuuviSensor)
    self.assertEqual(ruuvi.mac, 'AA:BB:CC:DD:EE:FF')
    assert isinstance(home_assistant, HomeAssistantSensor)
    self.assertIsNone(home_assistant.battery_sensor_id)
    self.assertIsNotNone(config.home_assistant)

  def test_ruuvi_mac_normalized_to_uppercase(self):
    lowercase = SENSORS_CONFIG.replace('"AA:BB:CC:DD:EE:FF"', '"aa:bb:cc:dd:ee:ff"')
    config_file = self._write_temp_config(VALID_CONFIG + lowercase)
    config = load_config(str(config_file))
    ruuvi = config.sensors[0]
    assert isinstance(ruuvi, RuuviSensor)
    self.assertEqual(ruuvi.mac, 'AA:BB:CC:DD:EE:FF')

  def test_too_many_sensors_fails(self):
    # SENSORS_CONFIG has 2 sensors, add 5 more
    ruuvi_sensor = SENSORS_CONFIG[SENSORS_CONFIG.index('[[sensors]]'):SENSORS_CONFIG.rindex('[[sensors]]')]
    config_file = self._write_temp_config(VALID_CONFIG + SENSORS_CONFIG + ruuvi_sensor * 5)
    with self.assertRaisesRegex(ConfigLoadError, r'sensors\s+List should have at most 6 items'):
      load_config(str(config_file))

  def test_invalid_ruuvi_mac_fails(self):
    invalid = SENSORS_CONFIG.replace('"AA:BB:CC:DD:EE:FF"', '"AA:BB:CC:DD:EE"')
    config_file = self._write_temp_config(VALID_CONFIG + invalid)
    with self.assertRaisesRegex(ConfigLoadError, r'sensors\.0\.Ruuvi\.mac\s+String should match pattern'):
      load_config(str(config_file))

  def test_sensor_without_type_fails(self):
    invalid = SENSORS_CONFIG.replace('type = "Ruuvi"\n', '')
    config_file = self._write_temp_config(VALID_CONFIG + invalid)
    with self.assertRaisesRegex(ConfigLoadError, r"sensors\.0\s+Unable to extract tag using discriminator 'type'"):
      load_config(str(config_file))


if __name__ == '__main__':
  unittest.main()
