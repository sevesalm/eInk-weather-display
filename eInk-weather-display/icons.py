import logging
from PIL import Image
from icon_mapping import observation_mapping, forecast_mapping, misc_icons

def get_weather_images():
  logger = logging.getLogger(__name__)
  logger.info('Importing icons')

  misc_images = {}
  for icon_name in misc_icons:
    misc_images[icon_name] = read_weather_icon(icon_name, None)
  misc_images['background'] = read_weather_icon('background', None)
  misc_images['background_day'] = read_weather_icon('background_day', None)
  misc_images['background_night'] = read_weather_icon('background_night', None)

  observation_images = {}
  for key, icon_set in observation_mapping.items():
    observation_images[key] = {'day': read_weather_icon(icon_set['day'], misc_images['background_day']) }
    night_icon = icon_set['night'] if ('night' in icon_set) else icon_set['day']
    observation_images[key]['night'] = read_weather_icon(night_icon, misc_images['background_night'])


  forecast_images = {}
  for key, icon_set in forecast_mapping.items():
    forecast_images[key] = { 'day': read_weather_icon(icon_set['day'], misc_images['background_day']) }
    night_icon = icon_set['night'] if ('night' in icon_set) else icon_set['day']
    forecast_images[key]['night'] = read_weather_icon(night_icon, misc_images['background_night'])


  return({ 
    "observation": observation_images, 
    "forecast": forecast_images, 
    "misc": misc_images,
  })

def read_weather_icon(icon_name, backgroun):
  mask = Image.open(f'png_icons/{icon_name}.png')
  icon = Image.new('RGBA', (mask.width, mask.height), '#ffffff00')
  if (backgroun != None):
    icon.paste(backgroun, (0,0), backgroun)
  icon.paste(mask, (0,0), mask)
  return icon

def get_scaled_image(image, new_width):
  height = int(image.height/image.width * new_width)
  return image.resize((new_width, height))