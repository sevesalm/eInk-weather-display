import datetime
import logging
import random
from ruuvitag_sensor.ruuvi_rx import RuuviTagReactive
from reactivex import operators as ops
from type_alias import SensorData
from app_config import AppConfig

logging.getLogger("bleson").setLevel(logging.ERROR)  # Suppress Bleson logging


def get_random_sensor_data(macs: list[str]) -> SensorData:
  return {mac: {"temperature": random.uniform(18, 30), "humidity": random.uniform(20, 80), "battery": random.uniform(2000, 3000), "rssi": random.uniform(-120, -10)} for mac in macs}


def get_sensor_data(logger: logging.Logger, config: AppConfig, macs: list[str]) -> SensorData:
  try:
    if (not (config.dev_mode_random_sensor_data and config.dev_mode)):
      ruuvis = RuuviTagReactive(macs)
      ruuvi_emissions = ruuvis.get_subject()
      missing_data = ruuvi_emissions.pipe(
                        ops.map(lambda x: x[0]),  # Only the mac address
                        ops.buffer_with_time(config.sensor_poll_timeout),  # Buffer for some time
                        ops.map(lambda x: set(x)),  # Convert macs into a set
                        ops.first(),
                        ops.flat_map(lambda x: list(set(macs).difference(x))),  # type: ignore # Emit once per each missing mac
                        ops.map(lambda x: (x, None))
                      )

      sensor_data = ruuvi_emissions.pipe(
                      ops.merge(missing_data),
                      ops.scan(lambda acc, x: acc | {x[0]: x[1]}, {}),
                      ops.filter(lambda x: len(x.keys()) == len(macs)),
                      ops.first()
                    ).run()

      ruuvis.stop()
      logger.info('Sensor data received: %s', repr(sensor_data))
      return {k: v for k, v in sensor_data.items() if v is not None}
    else:
      sensor_data = get_random_sensor_data(macs)
      logger.info('Using random sensor data: %s', repr(sensor_data))
      return sensor_data
  except Exception as e:
    logger.error('get_sensor_data() failed: %s', repr(e))
    return {}


# Logs stats about the sensor battery level
def log_sensor_data(sensor_data: SensorData, config: AppConfig) -> None:
  now = datetime.datetime.now()
  filename = config.sensor_data_log_filename
  # Logs battery levels at midnight
  if (now.hour == 0 and now.minute == 0):
    with open(filename, 'a') as f:
      log_rows = []
      if (config.ruuvitag_mac_in):
        log_rows.append(get_sensor_battery_log_string(sensor_data, config.ruuvitag_mac_in, config.ruuvitag_mac_in_name or 'In'))
      if (config.ruuvitag_mac_out):
        log_rows.append(get_sensor_battery_log_string(sensor_data, config.ruuvitag_mac_out, config.ruuvitag_mac_out_name or 'Out'))
      data_row = f'[{now.isoformat()}]: {", ".join(log_rows)}\n'
      f.write(data_row)


def get_sensor_battery_log_string(sensor_data: SensorData, mac: str, name: str) -> str:
  if mac not in sensor_data:
    return f'{name} N/A'
  return f'{name} {sensor_data[mac]["battery"]} mV'
