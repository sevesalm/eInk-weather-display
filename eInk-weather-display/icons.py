import logging
from PIL import Image
from icon_mapping import observation_mapping, weather_symbol_3_mapping, smart_symbol_mapping, misc_icons
from typing import Optional, Mapping
from type_alias import Icons, DayNightIcons


def get_weather_images() -> Icons:
  logger = logging.getLogger(__name__)
  logger.info('Importing icons')

  misc_images: Mapping[str, Image.Image] = {}
  for icon_name in misc_icons:
    misc_images[icon_name] = read_weather_icon(icon_name, None)
  misc_images['background'] = read_weather_icon('background', None)
  misc_images['background_day'] = read_weather_icon('background_day', None)
  misc_images['background_night'] = read_weather_icon('background_night', None)

  observation_images: Mapping[int, DayNightIcons] = {}
  for key, icon_set in observation_mapping.items():
    night_icon = icon_set['night'] if ('night' in icon_set) else icon_set['day']
    images: DayNightIcons = {
      'day': read_weather_icon(icon_set['day'], misc_images['background_day']),
      'night': read_weather_icon(night_icon, misc_images['background_night'])
    }
    observation_images[key] = images

  weather_symbol_3: Mapping[int, DayNightIcons] = {}
  for key, icon_set in weather_symbol_3_mapping.items():
    night_icon = icon_set['night'] if ('night' in icon_set) else icon_set['day']
    images: DayNightIcons = {
      'day': read_weather_icon(icon_set['day'], misc_images['background_day']),
      'night': read_weather_icon(night_icon, misc_images['background_night'])
    }
    weather_symbol_3[key] = images

  smart_symbol: Mapping[int, DayNightIcons] = {}
  for key, icon_set in smart_symbol_mapping.items():
    night_icon = icon_set['night'] if ('night' in icon_set) else icon_set['day']
    images: DayNightIcons = {
      'day': read_weather_icon(icon_set['day'], misc_images['background_day']),
      'night': read_weather_icon(night_icon, misc_images['background_night'])
    }
    smart_symbol[key] = images

  result: Icons = {
    "observation": observation_images,
    "weather_symbol_3": weather_symbol_3,
    "smart_symbol": smart_symbol,
    "misc": misc_images,
  }

  return result


def read_weather_icon(icon_name: str, background: Optional[Image.Image]) -> Image.Image:
  mask = Image.open(f'png_icons/{icon_name}.png')
  icon = Image.new('RGBA', (mask.width, mask.height), '#ffffff00')
  if (background is not None):
    icon.paste(background, (0, 0), background)
  icon.paste(mask, (0, 0), mask)
  return icon


def get_scaled_image(image: Image.Image, new_width: int) -> Image.Image:
  height = int(image.height/image.width * new_width)
  return image.resize((new_width, height))


def get_scaled_image_by_height(image: Image.Image, new_height: int) -> Image.Image:
  width = int(image.width/image.height * new_height)
  return image.resize((width, new_height))
