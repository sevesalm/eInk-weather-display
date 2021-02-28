from log import get_logger
from PIL import Image
from icon_mapping import observation_mapping, forecast_mapping, misc_icons

def get_weather_images(config):
  logger = get_logger(__name__)
  logger.info('Importing icons')
  icon_width = config.getint('ICON_WIDTH')
  observation_images = {}
  for key, icon_set in observation_mapping.items():
    observation_images[key] = {'day': read_weather_icon(icon_set['day'], icon_width) }
    if('night' in icon_set):
      observation_images[key]['night'] = read_weather_icon(icon_set['night'], icon_width)

  forecast_images = {}
  for key, icon_set in forecast_mapping.items():
    forecast_images[key] = { 'day': read_weather_icon(icon_set['day'], icon_width) }
    if('night' in icon_set):
      forecast_images[key]['night'] = read_weather_icon(icon_set['night'], icon_width)

  misc_images = {}
  for icon_name, icon_size in misc_icons:
    misc_images[icon_name] = read_weather_icon(icon_name, icon_size)
  return(observation_images, forecast_images, misc_images)

def read_weather_icon(icon_name, width):
  mask = Image.open(f'png_icons/{icon_name}.png')
  icon = Image.new('L', (mask.width, mask.height), 0xff)
  icon.paste(mask, (0,0), mask)
  height = int(icon.height/icon.width*width)
  return icon.resize((width, height))