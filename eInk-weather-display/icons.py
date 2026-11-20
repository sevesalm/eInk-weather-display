import logging
from timeit import default_timer as timer
from PIL import Image
from icon_mapping import observation_mapping, weather_symbol_3_mapping, smart_symbol_mapping
from typing import Mapping
from type_alias import Icons, DayNightIcons
from paths import APP_DIR

# Icons are pre-scaled at load to the size they're drawn at, so panels can paste them as is
OBSERVATION_ICON_SIZE = 280
FORECAST_ICON_SIZE = 200
CLOUD_COVER_ICON_SIZE = 160

MISC_ICON_WIDTHS = {
  'wind_icon': CLOUD_COVER_ICON_SIZE,
  'wind': 70,
  'temperature': 70,
  'humidity': 70,
  'pressure': 70,
  'warning': 50,
  **{f'cloud_cover_{i}': CLOUD_COVER_ICON_SIZE for i in range(10)},
}
MISC_ICON_HEIGHTS = {
  'temperature_feel': 70,
  'sunrise': 50,
}

# The observation panel picks these WeatherSymbol3 icons by cloud cover
OBSERVATION_CLOUD_COVER_SYMBOLS = [1, 2, 3]


def get_weather_images() -> Icons:
  logger = logging.getLogger(__name__)
  logger.info('Importing icons')
  start_time = timer()

  # The same icon is used in many mappings and for both day and night, so share the images.
  # Glyphs and backgrounds are scaled separately and composited at the target size, which needs far fewer resizes.
  glyphs: dict[tuple[str, int], Image.Image] = {}
  weather_icons: dict[tuple[str, str, int], Image.Image] = {}

  def get_glyph(icon_name: str, size: int) -> Image.Image:
    key = (icon_name, size)
    if key not in glyphs:
      glyphs[key] = get_scaled_image(read_icon(icon_name), size)
    return glyphs[key]

  def get_weather_icon(icon_name: str, variant: str, size: int) -> Image.Image:
    key = (icon_name, variant, size)
    if key not in weather_icons:
      icon = get_glyph(f'background_{variant}', size).copy()
      icon.alpha_composite(get_glyph(icon_name, size))
      weather_icons[key] = to_la(icon)
    return weather_icons[key]

  def get_icon_set(icon_set: Mapping[str, str], size: int) -> DayNightIcons:
    return {
      'day': get_weather_icon(icon_set['day'], 'day', size),
      'night': get_weather_icon(icon_set.get('night', icon_set['day']), 'night', size),
    }

  misc_images: dict[str, Image.Image] = {}
  for icon_name, width in MISC_ICON_WIDTHS.items():
    misc_images[icon_name] = to_la(get_scaled_image(read_icon(icon_name), width))
  for icon_name, height in MISC_ICON_HEIGHTS.items():
    misc_images[icon_name] = to_la(get_scaled_image_by_height(read_icon(icon_name), height))
  # Kept at full size for the missing icon fallback, which is drawn at different sizes
  misc_images['background_day'] = to_la(read_icon('background_day'))
  misc_images['background_night'] = to_la(read_icon('background_night'))

  result: Icons = {
    "observation": {key: get_icon_set(icon_set, OBSERVATION_ICON_SIZE) for key, icon_set in observation_mapping.items()},
    "observation_cloud_cover": {key: get_icon_set(weather_symbol_3_mapping[key], OBSERVATION_ICON_SIZE) for key in OBSERVATION_CLOUD_COVER_SYMBOLS},
    "weather_symbol_3": {key: get_icon_set(icon_set, FORECAST_ICON_SIZE) for key, icon_set in weather_symbol_3_mapping.items()},
    "smart_symbol": {key: get_icon_set(icon_set, FORECAST_ICON_SIZE) for key, icon_set in smart_symbol_mapping.items()},
    "misc": misc_images,
  }

  icon_count = len(misc_images) + len(weather_icons)
  logger.info(f'Imported {icon_count} icons in {timer() - start_time:.2f} s')
  return result


def read_icon(icon_name: str) -> Image.Image:
  with Image.open(APP_DIR / 'png_icons' / f'{icon_name}.png') as image:
    return image.convert('RGBA')


def to_la(image: Image.Image) -> Image.Image:
  '''Panels are grayscale, so gray + alpha is enough and takes half the memory of RGBA.'''
  return image.convert('LA')


def get_scaled_image(image: Image.Image, new_width: int) -> Image.Image:
  height = int(image.height/image.width * new_width)
  return image.resize((new_width, height))


def get_scaled_image_by_height(image: Image.Image, new_height: int) -> Image.Image:
  width = int(image.width/image.height * new_height)
  return image.resize((width, new_height))
