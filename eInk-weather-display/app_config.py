from __future__ import annotations

from pathlib import Path
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

try:
  import tomllib
except ModuleNotFoundError:
  import tomli as tomllib


class AppConfig(BaseModel):
  model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)

  dev_mode: bool
  dev_mode_output_filename: str

  dev_mode_random_weather_data: bool
  dev_mode_random_sensor_data: bool

  log_sensor_data: bool
  sensor_data_log_filename: str

  fmi_location: str
  fmi_observation_location_override: Optional[str] = None

  override_name: str
  override_latitude: float
  override_longitude: float

  draw_panel_borders: bool
  draw_borders: bool

  ruuvitag_mac_in: Optional[str] = None
  ruuvitag_mac_in_name: Optional[str] = None
  ruuvitag_mac_out: Optional[str] = None
  ruuvitag_mac_out_name: Optional[str] = None

  sensor_poll_timeout: int = Field(ge=0)

  rotate_180: bool
  mirror_horizontal: bool

  epd_model: Literal['7.8', '10.3']
  epd_voltage: int = Field(gt=0)
  bits_per_pixel: Literal[1, 2, 4]

  refresh_full_interval: int = Field(ge=1)
  refresh_partial_interval: int = Field(ge=1)

  high_temperature_warning_threshold: int
  extreme_high_temperature_warning_threshold: int
  low_temperature_warning_threshold: int
  extreme_low_temperature_warning_threshold: int
  tropical_night_temperature_warning_threshold: int

  @model_validator(mode='after')
  def validate_threshold_order(self) -> 'AppConfig':
    if self.low_temperature_warning_threshold > self.high_temperature_warning_threshold:
      raise ValueError('low_temperature_warning_threshold must be <= high_temperature_warning_threshold')

    if self.extreme_high_temperature_warning_threshold < self.high_temperature_warning_threshold:
      raise ValueError('extreme_high_temperature_warning_threshold must be >= high_temperature_warning_threshold')

    if self.extreme_low_temperature_warning_threshold > self.low_temperature_warning_threshold:
      raise ValueError('extreme_low_temperature_warning_threshold must be <= low_temperature_warning_threshold')

    return self


class ConfigLoadError(Exception):
  pass


def _read_toml(path: Path) -> dict[str, Any]:
  with path.open('rb') as file_obj:
    return tomllib.load(file_obj)


def load_config(path: str = 'config.ini') -> AppConfig:
  config_path = Path(path)
  try:
    raw_config = _read_toml(config_path)
  except FileNotFoundError as error:
    raise ConfigLoadError(f'Config file not found: {config_path}') from error
  except tomllib.TOMLDecodeError as error:
    raise ConfigLoadError(f'Invalid TOML in config file {config_path}: {error}') from error

  if 'general' not in raw_config or not isinstance(raw_config['general'], dict):
    raise ConfigLoadError('Config must contain a [general] table')

  try:
    return AppConfig.model_validate(raw_config['general'])
  except ValidationError as error:
    raise ConfigLoadError(f'Invalid config values: {error}') from error
