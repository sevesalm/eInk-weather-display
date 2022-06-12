from configparser import SectionProxy
import logging
import random
from ruuvitag_sensor.ruuvi_rx import RuuviTagReactive
from reactivex import operators as ops
from type_alias import SensorData


def get_sensor_data(logger: logging.Logger, config: SectionProxy, macs: list[str]) -> SensorData:
  try:
    if (not config.getboolean('USE_RANDOM_DATA')):
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
      sensor_data: SensorData = {mac: {"temperature": random.uniform(18, 30), "humidity": random.uniform(20, 80), "battery": random.uniform(2000, 3000), "rssi": random.uniform(-120, -10)} for mac in macs}
      logger.info('Using random sensor data: %s', repr(sensor_data))
      return sensor_data
  except Exception as e:
    logger.error('get_sensor_data() failed: %s', repr(e))
    return {}
