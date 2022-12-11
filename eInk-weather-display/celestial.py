# from typing import Final
import ephem
import math
import logging
import datetime
from zoneinfo import ZoneInfo
from typing import Optional, TypedDict
from type_alias import Datetime, Position
import enum


class Twilight(enum.IntEnum):
  DAYTIME = 0
  CIVIL = 1
  NAUTICAL = 2
  ASTRONOMICAL = 3
  NIGHT = 4


class DusksAndDawns(TypedDict):
    current_twilight: float
    times: list[Datetime]
    twilights: list[Twilight]


CIVIL_TWILIGHT_HORIZON = '-6'
NAUTICAL_TWILIGHT_HORIZON = '-12'
ASTRONOMICAL_TWILIGHT_HORIZON = '-18'


def get_is_daylight(position: Position, utc_datetime_string: str) -> bool:
  observer = ephem.Observer()
  observer.lat = position[0]
  observer.lon = position[1]
  observer.date = utc_datetime_string.replace('T', ' ').replace('+00:00', '').replace('Z', '')

  sun = ephem.Sun()   # type: ignore
  sun.compute(observer)
  is_above_horizon = sun.alt + sun.radius > 0
  return is_above_horizon


def get_observer(position: Position, aware_datetime: Datetime) -> ephem.Observer:
  observer = ephem.Observer()
  observer.lat = position[0]
  observer.lon = position[1]
  observer.date = aware_datetime.astimezone(tz=ZoneInfo('UTC'))
  return observer


def get_twilight(sun: ephem._sun) -> int:
  if (sun.alt + sun.radius > 0):
    return 0
  if (sun.alt >= ephem.degrees(CIVIL_TWILIGHT_HORIZON)):
    return 1
  if (sun.alt >= ephem.degrees(NAUTICAL_TWILIGHT_HORIZON)):
    return 2
  if (sun.alt >= ephem.degrees(ASTRONOMICAL_TWILIGHT_HORIZON)):
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
  sorted_times = sorted(times + [now])
  current_twilight_index = sorted(times + [now]).index(now)
  prev_time = sorted_times[current_twilight_index-1] if current_twilight_index > 0 else None
  next_time = sorted_times[current_twilight_index+1] if current_twilight_index < len(sorted_times) - 1 else None
  current_twilight = current_twilight_index + (0.5 if (not prev_time or not next_time) else (now-prev_time)/(next_time - prev_time))

  dawn_twilights = [Twilight(x) for x in list(range(transit_twilight + len(dawns), transit_twilight, -1))]
  dusk_twilights = [Twilight(x) for x in list(range(transit_twilight, transit_twilight + len(dusks) + 1))]
  twilights = dawn_twilights + dusk_twilights

  return {"current_twilight": current_twilight,
          "times": times,
          "twilights": twilights}


def get_twilight_length(twilight_data: DusksAndDawns, index: int) -> Optional[datetime.timedelta]:
  if (0 < index < len(twilight_data['twilights'])):
    return twilight_data['times'][index] - twilight_data['times'][index-1]
  return None


def get_daytime_length(twilight_data: DusksAndDawns) -> Optional[datetime.timedelta]:
  try:
    index = twilight_data['twilights'].index(Twilight.DAYTIME)
    return get_twilight_length(twilight_data, index)
  except ValueError:
    return None


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
