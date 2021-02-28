import math
from PIL import Image, ImageDraw, ImageOps
from log import get_logger
from weather import get_observations
from celestial import get_is_day
import utils

def get_observation_panel(location, observation_images, misc_images, fonts, config):
  logger = get_logger(__name__)
  (observations, first_position) = get_observations(location, 1)
  latest_date = max(observations.keys())
  isDay = get_is_day(first_position, latest_date)
  x_size = 220
  y_size = 100
  latest = observations[latest_date]
  logger.info(latest)
  image = Image.new('L', (x_size, y_size), 0xff) 
  draw = ImageDraw.Draw(image)
  
  delimiter_x = 80
  data_y_base = 15
  # Temperature
  utils.draw_quantity(draw, (delimiter_x, data_y_base + 5), str(latest["t2m"]), '°C', fonts, 'font_lg')

  # Wind direction and speed
  if(not math.isnan(latest['wd_10min'])):
    wind_image = misc_images['wind_arrow']
    wind_image_rot = wind_image.rotate(-latest['wd_10min'] + 180, fillcolor = 0xff)
    image.paste(wind_image_rot, (delimiter_x - 60 - wind_image.width//2, data_y_base + 30 - wind_image.height//2), ImageOps.invert(wind_image_rot))
  utils.draw_quantity(draw, (delimiter_x, data_y_base + 30), str(latest["ws_10min"]), 'm/s', fonts)

  # Relative humidity
  utils.draw_quantity(draw, (delimiter_x, data_y_base + 50), str(latest["rh"]), '%', fonts)

  # Barometric pressure
  utils.draw_quantity(draw, (delimiter_x, data_y_base + 70), str(latest["p_sea"]), 'hPa', fonts)
  
  # Weather icon
  weather_symbol = latest['wawa']
  randomize_weather_icons = config.getboolean('RANDOMIZE_WEATHER_ICONS')
  if(not math.isnan(weather_symbol) and weather_symbol in observation_images or randomize_weather_icons):
    if(not randomize_weather_icons):
      image_set = observation_images.get(weather_symbol)
    else:
      image_set = observation_images[random.choice(list(observation_images.keys()))]
    if(not isDay and 'night' in image_set):
      weather_icon = image_set['night']
    else:
      weather_icon = image_set['day']
    image.paste(weather_icon, (int(3*x_size/4 - weather_icon.width/2), int(y_size/2 - weather_icon.height/2)))
  else:
    draw.text((int(3*x_size/4), int(y_size/2)), f'(NA: {weather_symbol})', font = fonts['font_sm'], fill = 0, anchor = 'mm')

  # Borders
  if (config.getboolean('DRAW_PANEL_BORDERS')):
    draw.polygon([(0, 0), (x_size-1, 0), (x_size-1, y_size-1), (0, y_size-1), (0, 0)])
    
  return image