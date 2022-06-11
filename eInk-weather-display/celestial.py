# from typing import Final
import ephem
import math
import logging
import datetime
from zoneinfo import ZoneInfo
from typing import Optional, TypedDict
from type_alias import Datetime, Position


class DusksAndDawns(TypedDict):
    now_index: int
    times: list[Datetime]
    twilights: list[int]


CIVIL_TWILIGHT_HORIZON = '-6'
NAUTICAL_TWILIGHT_HORIZON = '-12'
ASTRONOMICAL_TWILIGHT_HORIZON = '-18'


def get_is_daylight(position: Position, utc_datetime_string: str) -> bool:
  location = ephem.Observer()
  location.lat = position[0]
  location.lon = position[1]
  location.date = utc_datetime_string.replace('T', ' ').replace('+00:00', '').replace('Z', '')

  sun = ephem.Sun()   # type: ignore
  sunset = ephem.localtime(location.next_setting(sun))
  sunrise = ephem.localtime(location.next_rising(sun))
  return (sunset < sunrise)


def get_observer(position: Position, aware_datetime: Datetime) -> ephem.Observer:
  observer = ephem.Observer()
  observer.lat = position[0]
  observer.lon = position[1]
  observer.date = aware_datetime.astimezone(tz=ZoneInfo('UTC'))
  return observer


def get_twilight(sun: ephem._sun) -> int:
  if(sun.alt + sun.radius > 0):
    return 0
  if(sun.alt >= ephem.degrees(CIVIL_TWILIGHT_HORIZON)):
    return 1
  if(sun.alt >= ephem.degrees(NAUTICAL_TWILIGHT_HORIZON)):
    return 2
  if(sun.alt >= ephem.degrees(ASTRONOMICAL_TWILIGHT_HORIZON)):
    return 3
  return 4


def get_nearest_sun_transit(position: Position, aware_datetime: Datetime) -> tuple[Datetime, int]:
  observer = get_observer(position, aware_datetime)
  sun = ephem.Sun()  # type: ignore

  next_transit = ephem.localtime(observer.next_transit(sun)).astimezone(tz=None)
  previous_transit = ephem.localtime(observer.previous_transit(sun)).astimezone(tz=None)
  is_next_transit_closer = abs(aware_datetime-next_transit) <= abs(aware_datetime-previous_transit)
  nearest_transit = next_transit if (is_next_transit_closer) else previous_transit
  observer.date = nearest_transit.astimezone(tz=ZoneInfo('UTC'))
  sun.compute(observer)
  transit_twilight = get_twilight(sun)
  return (nearest_transit, transit_twilight)


def remove_odd(transit_datetime: Datetime, d: Datetime) -> Optional[Datetime]:
  return d if abs(transit_datetime - d) < datetime.timedelta(days=1) else None


def get_previous_rising(location: ephem.Observer, sun: ephem._sun, transit_datetime: Datetime, use_center: bool = False) -> Optional[Datetime]:
  try:
    d = ephem.localtime(location.previous_rising(sun, use_center=use_center)).astimezone(tz=None)
    return remove_odd(transit_datetime, d)
  except (ephem.NeverUpError, ephem.AlwaysUpError):
    return None


def get_next_setting(location: ephem.Observer, sun: ephem._sun, transit_datetime: Datetime, use_center: bool = False) -> Optional[Datetime]:
  try:
    d = ephem.localtime(location.next_setting(sun, use_center=use_center)).astimezone(tz=None)
    return remove_odd(transit_datetime, d)
  except (ephem.NeverUpError, ephem.AlwaysUpError):
    return None


def get_dusks_and_dawns(position: Position, now: Datetime) -> DusksAndDawns:
  location = ephem.Observer()
  location.lat = position[0]
  location.lon = position[1]
  (transit_datetime, transit_twilight) = get_nearest_sun_transit(position, now)
  location.date = transit_datetime.astimezone(tz=ZoneInfo('UTC'))

  sun = ephem.Sun()  # type: ignore
  previous_sunrise = get_previous_rising(location, sun, transit_datetime)
  next_sunset = get_next_setting(location, sun, transit_datetime)

  location.horizon = CIVIL_TWILIGHT_HORIZON
  civil_dawn = get_previous_rising(location, sun, transit_datetime, True)
  civil_dusk = get_next_setting(location, sun, transit_datetime, True)

  location.horizon = NAUTICAL_TWILIGHT_HORIZON
  nautical_dawn = get_previous_rising(location, sun, transit_datetime, True)
  nautical_dusk = get_next_setting(location, sun, transit_datetime, True)

  location.horizon = ASTRONOMICAL_TWILIGHT_HORIZON
  astronomical_dawn = get_previous_rising(location, sun, transit_datetime, True)
  astronomical_dusk = get_next_setting(location, sun, transit_datetime, True)

  dawns = [x for x in [astronomical_dawn, nautical_dawn, civil_dawn, previous_sunrise] if x is not None]
  dusks = [x for x in [next_sunset, civil_dusk, nautical_dusk, astronomical_dusk] if x is not None]

  times = dawns + dusks
  now_index = sorted(times + [now]).index(now)

  dawn_twilights = list(range(transit_twilight + len(dawns), transit_twilight, -1))
  dusk_twilights = list(range(transit_twilight, transit_twilight + len(dusks) + 1))
  twilights = dawn_twilights + dusk_twilights

  return {"now_index": now_index,
          "times": times,
          "twilights": twilights}


def get_moon_phase() -> tuple[int, float]:
  moon = ephem.Moon()
  moon.compute()
  phase = int(round(moon.elong.norm*180/ephem.pi))
  return (phase, moon.phase)


def get_moon_phase_chr(moon_phase_deg: float) -> str:
  """Returns the unicode character base on the moon phase in degrees.

  Note: The font has 40 moon icons spaced evenly based on the cosine of the moonphase.
  The mapping has to done likewise using cosine. Cosine mapping done to get even visual
  difference between icons.
  0:   New moon
  180: Full moon
  """
  logger = logging.getLogger(__name__)
  base = 0xe900
  delta = round(10 * math.cos(math.radians(moon_phase_deg)))
  if (moon_phase_deg < 180):
    index = 10 - delta
  else:
    index = (30 + delta) % 40
  logger.debug("Moon phase: %d, index: %d", moon_phase_deg, index)
  return chr(base + index)
