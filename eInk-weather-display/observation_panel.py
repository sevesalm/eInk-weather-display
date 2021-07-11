import math
import random
from PIL import Image, ImageDraw
import logging
from weather import get_observations
from celestial import get_is_daylight
import utils
import icons

def get_observation_icon(wawa, cloud_coverage, is_daylight, images, fonts, config):
  if (config.getboolean('RANDOMIZE_WEATHER_ICONS')):
    icon_set = images['observation'][random.choice(list(images['observation'].keys()))]
    return utils.get_icon_variant(is_daylight, icon_set)

  if (not wawa in images['observation']):
    return utils.get_missing_weather_icon_icon(wawa, images, fonts)

  # For codes 0 to 3 and 20 to 26, let's use cloud cover to determine the icon set
  if(((0 <= wawa <= 3) or (20 <= wawa <= 26)) and not math.isnan(cloud_coverage)):
    if(cloud_coverage <= 1): # Clear sky
      icon_set = images['forecast'].get(1)
    elif(2 <= cloud_coverage <= 6): # Partially cloudy
      icon_set = images['forecast'].get(2)
    elif(7 <= cloud_coverage <= 8): # Overcast
      icon_set = images['forecast'].get(3)
    else: # Lolwut?
      icon_set = images['observation'].get(0)
  else:
    icon_set = images['observation'].get(wawa)
  return utils.get_icon_variant(is_daylight, icon_set)

def get_observation_panel(location, images, fonts, config):
  logger = logging.getLogger(__name__)
  logger.info('Generating observation panel')
  icon_width = config.getint('ICON_WIDTH')
  (observations, first_position, first_position_name) = get_observations(location, 1)
  logger.info('Received data: %s', repr(observations))
  latest_date = max(observations.keys())
  isDay = get_is_day(first_position, latest_date)
  x_size = 650
  y_size = 550
  latest = observations[latest_date]
  image = Image.new('L', (x_size, y_size), 0xff) 
  draw = ImageDraw.Draw(image)

  utils.draw_title(draw, fonts['font_sm'], 'OUT', first_position_name, fonts['font_xxs'])

  delimiter_x = 525
  data_y_base = 100

  # Temperature
  utils.draw_quantity(draw, (delimiter_x, data_y_base + 120), str(latest["t2m"]), '°C', fonts, 'font_lg', 'font_sm')

  # Relative humidity
  utils.draw_quantity(draw, (delimiter_x, data_y_base + 210), str(round(latest["rh"])), '%', fonts)

  # Barometric pressure
  utils.draw_quantity(draw, (delimiter_x, data_y_base + 280), str(round(latest["p_sea"])), 'hPa', fonts)
  
  # Wind speed
  utils.draw_quantity(draw, (delimiter_x, data_y_base + 350), f'{round(latest["ws_10min"])} – {round(latest["wg_10min"])}', 'm/s', fonts)

  # Weather icon
  cloud_coverage = latest['n_man']

  weather_icon = icons.get_scaled_image(get_observation_icon(latest['wawa'], cloud_coverage, is_daylight, images, fonts, config), icon_width)
  image.paste(weather_icon, (15, data_y_base), weather_icon)

  # Warning icon
  if (latest["t2m"] >= config.getint('HIGH_TEMPERATURE_WARNING_THRESHOLD') or latest["t2m"] <= config.getint('LOW_TEMPERATURE_WARNING_THRESHOLD')):
    warning_icon = icons.get_scaled_image(images['misc']['warning'], 50)
    image.paste(warning_icon, (15 + weather_icon.width - 2*warning_icon.width//3, data_y_base + weather_icon.height - 2*warning_icon.height//3), warning_icon)

  row_y_base = 100

  # Cloud cover
  cloud_cover_icon = icons.get_scaled_image(utils.get_cloud_cover_icon(cloud_coverage, images, fonts, config), 160)
  image.paste(cloud_cover_icon, (15 + config.getint('ICON_WIDTH')//2 - cloud_cover_icon.width//2, data_y_base + 120 + row_y_base), cloud_cover_icon)

  # Wind direction
  w_dir = latest['wd_10min']
  if(not math.isnan(w_dir)):
    wind_image = icons.get_scaled_image(images['misc']['wind_icon'], 160)
    wind_image_rot = wind_image.rotate(-w_dir + 180, fillcolor = 0xff, resample=Image.BICUBIC)
    image.paste(wind_image_rot, (15 + config.getint('ICON_WIDTH')//2 - cloud_cover_icon.width//2, data_y_base + 120 + row_y_base), wind_image_rot)


  # Borders
  if (config.getboolean('DRAW_PANEL_BORDERS')):
    draw.polygon([(0, 0), (x_size-1, 0), (x_size-1, y_size-1), (0, y_size-1), (0, 0)])
    
  return image
