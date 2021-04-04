import ephem
import math
import logging

def get_is_day(position, utc_datetime):
  location = ephem.Observer()
  location.lat = str(position[0])
  location.lon = str(position[1])
  location.date = utc_datetime.replace('T', ' ').replace('Z', '')

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
  isDay = sunset < sunrise
  if(not isDay):
    return (sunrise, sunset)
  return (ephem.localtime(location.previous_rising(sun)), sunset) # Return the previous if sunset has not happened but sunrise has

def get_moon_phase():
  moon = ephem.Moon()
  moon.compute()
  phase = int(round(moon.elong.norm*180/ephem.pi))
  return (phase, moon.phase)

def get_moon_phase_icon(moon_phase_deg, images):
  logger = logging.getLogger(__name__)
  logger.debug("Moon phase: %d", moon_phase_deg)
  index = (round(moon_phase_deg/15) * 15) % 360
  icon_name = f'moon_{index}'
  logger.debug("Moon phase icon name: %s", icon_name)
  return images['moon'][icon_name]