import os
# Use Bleson adapter as the default BlueZ adapter causes random crashes and does not recover 
os.environ["RUUVI_BLE_ADAPTER"] = "bleson"

import datetime
from configparser import SectionProxy
import logging
import random
from ruuvitag_sensor.ruuvi_rx import RuuviTagReactive
from reactivex import operators as ops
from type_alias import SensorData

logging.getLogger("bleson").setLevel(logging.ERROR) # Suppress Bleson logging

def get_random_sensor_data(macs: list[str]) -> SensorData:
  return {mac: {"temperature": random.uniform(18, 30), "humidity": random.uniform(20, 80), "battery": random.uniform(2000, 3000), "rssi": random.uniform(-120, -10)} for mac in macs}


def get_sensor_data(logger: logging.Logger, config: SectionProxy, macs: list[str]) -> SensorData:
  try:
    if (not (config.getboolean('DEV_MODE_RANDOM_SENSOR_DATA') and config.getboolean('DEV_MODE'))):
      ruuvis = RuuviTagReactive(macs)
      ruuvi_emissions = ruuvis.get_subject()
      missing_data = ruuvi_emissions.pipe(
                        ops.map(lambda x: x[0]),  # Only the mac address
                        ops.buffer_with_time(config.getint('SENSOR_POLL_TIMEOUT')),  # Buffer for some time
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
def log_sensor_data(sensor_data: SensorData, config: SectionProxy) -> None:
  now = datetime.datetime.now()
  filename = config.get('SENSOR_DATA_LOG_FILENAME')
  # Logs battery levels at midnight
  if (now.hour == 0 and now.minute == 0):
    with open(filename, 'a') as f:
      mac_in = config.get('RUUVITAG_MAC_IN')
      name_in = config.get('RUUVITAG_MAC_IN_NAME')
      mac_out = config.get('RUUVITAG_MAC_OUT')
      name_out = config.get('RUUVITAG_MAC_OUT_NAME')
      log_str_in = get_sensor_battery_log_string(sensor_data, mac_in, name_in)
      log_str_out = get_sensor_battery_log_string(sensor_data, mac_out, name_out)
      data_row = f'[{now.isoformat()}]: {log_str_in}, {log_str_out}\n'
      f.write(data_row)


def get_sensor_battery_log_string(sensor_data: SensorData, mac: str, name: str):
  return f'{name} {sensor_data[mac]["battery"]} mV'