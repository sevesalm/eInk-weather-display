from __future__ import annotations

import json
import logging
import requests
from typing import TYPE_CHECKING, Any, Optional
from uuid import UUID

from pydantic import BaseModel, field_validator, ValidationError

from sensor_data import get_ruuvi_sensor_data

if TYPE_CHECKING:
  from app_config import AppConfig, HomeAssistantSensor, RuuviSensor

REQUEST_TIMEOUT = 5


class SensorReading(BaseModel):
  """Validated sensor reading from Home Assistant or Ruuvi."""
  temperature: Optional[float] = None
  humidity: Optional[float] = None
  battery: Optional[float] = None
  rssi: Optional[float] = None

  @field_validator('temperature', 'humidity', 'battery', mode='before')
  @classmethod
  def convert_unknown_to_none(cls, v: Any) -> Optional[float]:
    if v == "unknown" or v == "unavailable" or v == "":
      return None
    if isinstance(v, str):
      try:
        return float(v)
      except ValueError:
        return None
    return v


def get_sensor_data(config: AppConfig, logger: logging.Logger) -> dict[UUID, SensorReading | None]:
  """Fetch sensor data for all configured sensors, keyed by sensor id in config order."""
  data = get_home_assistant_sensor_data(config, logger) | get_ruuvi_sensor_readings(config, logger)
  return {sensor.id: data.get(sensor.id) for sensor in config.sensors}


def get_ruuvi_sensor_readings(config: AppConfig, logger: logging.Logger) -> dict[UUID, SensorReading | None]:
  """Fetch sensor data for all Ruuvi type sensors."""
  ruuvi_sensors: list[RuuviSensor] = [
    sensor for sensor in config.sensors if sensor.type == "Ruuvi"
  ]

  if not ruuvi_sensors:
    logger.info("No Ruuvi sensors configured")
    return {}

  # The same MAC may be configured for several sensors, so poll each only once
  macs = list(dict.fromkeys(sensor.mac for sensor in ruuvi_sensors))
  ruuvi_data = get_ruuvi_sensor_data(logger, config, macs)

  result: dict[UUID, SensorReading | None] = {}
  for sensor in ruuvi_sensors:
    reading = ruuvi_data.get(sensor.mac)
    try:
      result[sensor.id] = SensorReading.model_validate(reading) if reading is not None else None
    except ValidationError as e:
      logger.error(f"Failed to validate Ruuvi sensor data for {sensor.mac}: {e}")
      result[sensor.id] = None

  return result


def get_home_assistant_sensor_data(config: AppConfig, logger: logging.Logger) -> dict[UUID, SensorReading | None]:
  """Fetch sensor data from Home Assistant for all HomeAssistant type sensors."""
  # Filter sensors to only HomeAssistant type
  ha_sensors: list[HomeAssistantSensor] = [
    sensor for sensor in config.sensors if sensor.type == "HomeAssistant"
  ]

  if not ha_sensors:
    logger.info("No HomeAssistant sensors configured")
    return {}

  logger.info("Fetching sensor data from Home Assistant")
  if config.home_assistant is None:
    logger.info("Home Assistant config not set")
    return {}

  # Build a Jinja template that renders all sensor states as a JSON object. Identifiers are
  # embedded as JSON string literals (valid Jinja literals) and the output is serialized with
  # tojson, so quotes or backslashes in states or entity ids can't break the response.
  sensor_entries = []
  for sensor in ha_sensors:
    sensor_entries.append(
      f'{json.dumps(str(sensor.id))}: {{'
      f'"temperature": states({json.dumps(sensor.temperature_sensor_id)}), '
      f'"humidity": states({json.dumps(sensor.humidity_sensor_id)}), '
      f'"battery": states({json.dumps(str(sensor.battery_sensor_id))})'
      f'}}'
    )

  template_content = "{{ {" + ", ".join(sensor_entries) + "} | tojson }}"
  payload = {"template": template_content}

  url = f"{str(config.home_assistant.url).rstrip('/')}/api/template"
  headers = {
    "Authorization": f"Bearer {config.home_assistant.bearer_token}",
    "Content-Type": "application/json",
  }

  try:
    response = requests.post(url, headers=headers, json=payload, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
  except requests.RequestException as e:
    logger.error(f"Failed to fetch Home Assistant sensor data: {e}")
    return {}

  try:
    raw_data = json.loads(response.text)
  except json.JSONDecodeError as e:
    logger.error(f"Failed to parse Home Assistant response: {e}")
    return {}

  if not isinstance(raw_data, dict):
    logger.error(f"Unexpected Home Assistant response: {raw_data!r}")
    return {}

  # Validate each sensor separately so one malformed entry doesn't drop the others
  result: dict[UUID, SensorReading | None] = {}
  for sensor in ha_sensors:
    reading = raw_data.get(str(sensor.id))
    try:
      result[sensor.id] = SensorReading.model_validate(reading) if reading is not None else None
    except ValidationError as e:
      logger.error(f"Failed to validate Home Assistant sensor data for {sensor.name}: {e}")
      result[sensor.id] = None

  logger.info(f"Home Assistant sensor data: {result}")
  return result
