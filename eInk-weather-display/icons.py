import logging
from PIL import Image
from icon_mapping import observation_mapping, forecast_mapping, misc_icons

def get_weather_images():
  logger = logging.getLogger(__name__)
  logger.info('Importing icons')
  observation_images = {}
  for key, icon_set in observation_mapping.items():
    observation_images[key] = {'day': read_weather_icon(icon_set['day'], True) }
    if('night' in icon_set):
      observation_images[key]['night'] = read_weather_icon(icon_set['night'], True)

  forecast_images = {}
  for key, icon_set in forecast_mapping.items():
    forecast_images[key] = { 'day': read_weather_icon(icon_set['day'], True) }
    if('night' in icon_set):
      forecast_images[key]['night'] = read_weather_icon(icon_set['night'], True)

  misc_images = {}
  for icon_name in misc_icons:
    misc_images[icon_name] = read_weather_icon(icon_name, False)
  misc_images['background'] = read_weather_icon('background', False)

  return({ 
    "observation": observation_images, 
    "forecast": forecast_images, 
    "misc": misc_images,
  })

def read_weather_icon(icon_name, apply_background):
  mask = Image.open(f'png_icons/{icon_name}.png')
  background = Image.open('png_icons/background.png')
  icon = Image.new('RGBA', (mask.width, mask.height), '#ffffff00')
  if (apply_background == True):
    icon.paste(background, (0,0), background)
  icon.paste(mask, (0,0), mask)
  return icon

def get_scaled_image(image, new_width):
  height = int(image.height/image.width * new_width)
  return image.resize((new_width, height))