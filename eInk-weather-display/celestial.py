import ephem
import math
import logging

def get_is_daylight(position, utc_datetime_string):
  location = ephem.Observer()
  location.lat = str(position[0])
  location.lon = str(position[1])
  location.date = utc_datetime_string.replace('T', ' ').replace('Z', '')

  sun = ephem.Sun()
  sunset = ephem.localtime(location.next_setting(sun))
  sunrise = ephem.localtime(location.next_rising(sun))
  return (sunset < sunrise)

def get_sunrise_sunset(position):
  location = ephem.Observer()
  location.lat = str(position[0])
  location.lon = str(position[1])

  sun = ephem.Sun()
  sunset = ephem.localtime(location.next_setting(sun))
  sunrise = ephem.localtime(location.next_rising(sun))
  is_daylight = sunset < sunrise
  if(not is_daylight):
    return (sunrise, sunset)
  return (ephem.localtime(location.previous_rising(sun)), sunset) # Return the previous if sunset has not happened but sunrise has

def get_moon_phase():
  moon = ephem.Moon()
  moon.compute()
  phase = int(round(moon.elong.norm*180/ephem.pi))
  return (phase, moon.phase)

def get_moon_phase_chr(moon_phase_deg):
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