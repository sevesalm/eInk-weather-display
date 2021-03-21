import math
import random
from PIL import Image, ImageDraw, ImageOps
import logging
from weather import get_observations
from celestial import get_is_day
import utils

def get_observation_icon(randomize_weather_icons, cloud_coverage, images, weather_symbol, isDay):
  if(not randomize_weather_icons):
    # For codes 0 to 3 and 20 to 26, let's use cloud cover to determine the icon set
    if(((0 <= weather_symbol <= 3) or (20 <= weather_symbol <= 26)) and not math.isnan(cloud_coverage)):
      if(cloud_coverage <= 1): # Clear sky
        image_set = images['forecast'].get(1)
      elif(2 <= cloud_coverage <= 6): # Partially cloudy
        image_set = images['forecast'].get(2)
      elif(7 <= cloud_coverage <= 8): # Overcast
        image_set = images['forecast'].get(3)
      else: # Lolwut?
        image_set = images['observation'].get(0)
    else:
      image_set = images['observation'].get(weather_symbol)
  else:
    image_set = images['observation'][random.choice(list(images['observation'].keys()))]

  if(not isDay and 'night' in image_set):
    weather_icon = image_set['night']
  else:
    weather_icon = image_set['day']

  return weather_icon

def get_observation_panel(location, images, fonts, config):
  logger = logging.getLogger(__name__)
  logger.info('Generating observation panel')
  (observations, first_position) = get_observations(location, 1)
  logger.info('Received data: %s', repr(observations))
  latest_date = max(observations.keys())
  isDay = get_is_day(first_position, latest_date)
  x_size = 200
  y_size = 100
  latest = observations[latest_date]
  image = Image.new('L', (x_size, y_size), 0xff) 
  draw = ImageDraw.Draw(image)
  
  delimiter_x = 150
  data_y_base = 15
  # Temperature
  utils.draw_quantity(draw, (delimiter_x, data_y_base + 5), str(latest["t2m"]), '°C', fonts, 'font_lg')

  # Relative humidity
  utils.draw_quantity(draw, (delimiter_x, data_y_base + 30), str(latest["rh"]), '%', fonts)

  # Barometric pressure
  utils.draw_quantity(draw, (delimiter_x, data_y_base + 50), str(latest["p_sea"]), 'hPa', fonts)
  
  # Wind speed
  utils.draw_quantity(draw, (delimiter_x, data_y_base + 70), str(latest["ws_10min"]), 'm/s', fonts)

  # Weather icon
  weather_symbol = latest['wawa']
  cloud_coverage = latest['n_man']
  randomize_weather_icons = config.getboolean('RANDOMIZE_WEATHER_ICONS')
  if(not math.isnan(weather_symbol) and weather_symbol in images['observation'] or randomize_weather_icons):
    weather_icon = get_observation_icon(randomize_weather_icons, cloud_coverage, images, weather_symbol, isDay)
    image.paste(weather_icon, (15, 0))
  else:
    draw.text((15 + config.getint('ICON_WIDTH')//2, config.getint('ICON_WIDTH')//2), f'(NA: {weather_symbol})', font = fonts['font_sm'], fill = 0, anchor = 'mm')
  # Wind direction and speed
  if(not math.isnan(latest['wd_10min'])):
    wind_image = images['misc']['wind_arrow']
    wind_image_rot = wind_image.rotate(-latest['wd_10min'] + 180, fillcolor = 0xff, resample=Image.BICUBIC)
    image.paste(wind_image_rot, (15 + config.getint('ICON_WIDTH')//2 - wind_image.width//2, y_size - wind_image.height), ImageOps.invert(wind_image_rot))

  # Borders
  if (config.getboolean('DRAW_PANEL_BORDERS')):
    draw.polygon([(0, 0), (x_size-1, 0), (x_size-1, y_size-1), (0, y_size-1), (0, 0)])
    
  return image