import sys
import math
import ctypes
from PIL import ImageFont, ImageDraw, Image, features
from dateutil.parser import parse
from zoneinfo import ZoneInfo
from configparser import SectionProxy
from typing import Optional, Union
from type_alias import Datetime, Fonts, Icons, DayNightIcons, WeatherWarning, Position
from datetime import datetime, timedelta
import logging

SUPPORTED_EPD_MODELS = ['7.8', '10.3']
NAN_SYMBOL = '?'


def draw_quantity(draw: ImageDraw.ImageDraw, mid_point: tuple[int, int], value: str, unit: str, fonts: Fonts, font: str = 'font_sm', font_unit: str = 'font_xs') -> None:
  (x, y) = mid_point
  draw.text((x - 7, y), value, font=fonts[font], fill=0, anchor='rs')
  draw.text((x + 7, y), unit, font=fonts[font_unit], fill=0, anchor='ls')


def draw_time(draw: ImageDraw.ImageDraw, coordinate: tuple[int, int], minutes: str, hours: str, font: ImageFont.FreeTypeFont) -> None:
  offset = font.size//8
  draw.text(coordinate, ":", font=font, fill=0, anchor='mm')
  draw.text((coordinate[0]+offset, coordinate[1]), minutes, font=font, fill=0, anchor='lm', features=["tnum"])
  draw.text((coordinate[0]-offset, coordinate[1]), hours, font=font, fill=0, anchor='rm', features=["tnum"])


def check_raqm_support(logger: logging.Logger) -> None:
  '''Check if the Raqm support is enabled. Used to enable OpenType font features.'''
  is_raqm_supported = features.check_feature('raqm')
  if is_raqm_supported:
    logger.info("Raqm support detected")
  else:
    logger.warn('Raqm not supported')


def check_python_version() -> None:
  major = sys.version_info[0]
  minor = sys.version_info[1]
  if major < 3 or minor < 7:
    raise Exception('Python 3.7 or newer required')


def from_8bit_to_2bit(image: Image.Image) -> bytes:
  '''Converts a 8-bit image into a packed 2-bit image which can be fed to EPD.'''
  if (image.mode != 'L'):
    raise Exception('Image mode must be \'L\'')
  if (image.width % 4 != 0):
    raise Exception('Image width % 4 must be 0')

  image_bytes = image.tobytes()
  result = bytearray()
  for y in range(image.height):
    for x in range(image.width // 4):
      px0 = (image_bytes[y*image.width + x*4 + 0] & (0x3 << 6)) >> 0
      px1 = (image_bytes[y*image.width + x*4 + 1] & (0x3 << 6)) >> 2
      px2 = (image_bytes[y*image.width + x*4 + 2] & (0x3 << 6)) >> 4
      px3 = (image_bytes[y*image.width + x*4 + 3] & (0x3 << 6)) >> 6

      new_px = px0 | px1 | px2 | px3
      result.append(new_px)
  return bytes(result)


def get_epd_data(config: SectionProxy) -> tuple[Optional[ctypes.CDLL], tuple[int, int]]:
  if (is_supported_epd(config.get('EPD_MODEL'))):
    if (config.getboolean('DEV_MODE')):
      return (None, (1872, 1404))
    else:
      return (ctypes.CDLL("lib/epd78.so"), (1872, 1404))
  else:
    raise Exception(f'Unsupported model: {config.get("EPD_MODEL")}')


def get_fonts(config: SectionProxy) -> Fonts:
  if (is_supported_epd(config.get('EPD_MODEL'))):
    font_mult = 4
  else:
    raise Exception(f'Unsupported model: {config.get("EPD_MODEL")}')

  return {
    'font_lg': ImageFont.truetype('fonts/regular.woff', font_mult * 42),
    'font_md': ImageFont.truetype('fonts/regular.woff', font_mult * 32),
    'font_sm': ImageFont.truetype('fonts/regular.woff', font_mult * 18),
    'font_sm_bold': ImageFont.truetype('fonts/bold.woff', font_mult * 18),
    'font_xs': ImageFont.truetype('fonts/regular.woff', font_mult * 14),
    'font_xxs': ImageFont.truetype('fonts/regular.woff', font_mult * 9),
    'font_misc_md': ImageFont.truetype('fonts/misc.woff', font_mult * 32)
  }


def get_text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> tuple[int, int]:
  b_box = draw.textbbox((0, 0), text, font)
  return (b_box[2] - b_box[0], b_box[3] - b_box[1])


def draw_title(draw: ImageDraw.ImageDraw, title_font: ImageFont.FreeTypeFont, title: str, sub_title: Optional[str] = None, sub_title_font: Optional[ImageFont.FreeTypeFont] = None) -> None:
  size_width, size_height = get_text_size(draw, title, title_font)
  x_padding = 20
  y_padding = 8
  y_offset = -3  # To actually center the title

  draw.rectangle(((0, 0), (size_width + x_padding, size_height + y_padding)), fill=0x00)
  draw.text(((size_width + x_padding)//2, (size_height + y_padding)//2 + y_offset), title, fill="white", font=title_font, anchor='mm')
  if (sub_title):
    if (not sub_title_font):
      sub_title_font = title_font
    sub_title_size_width, _ = get_text_size(draw, sub_title, sub_title_font)
    draw.rectangle(((size_width + x_padding, 0), (size_width + x_padding + sub_title_size_width + 40, size_height + y_padding)), fill=0xff, outline=0, width=4)
    draw.text(((size_width + x_padding + (sub_title_size_width + 40)//2), (size_height + y_padding)//2), sub_title, fill="black", font=sub_title_font, anchor='mm')


def get_icon_variant(is_daylight: bool, icon_set: DayNightIcons) -> Image.Image:
  if (not is_daylight and 'night' in icon_set):
    return icon_set['night']
  return icon_set['day']


def get_missing_weather_icon_icon(icon_index: Union[float, int], is_daylight: bool, images: Icons, fonts: Fonts) -> Image.Image:
  icon = images['misc']['background_day'].copy() if is_daylight else images['misc']['background_night'].copy()
  draw = ImageDraw.Draw(icon)
  text = "NaN" if math.isnan(icon_index) else str(icon_index)
  draw.text((icon.width//2, icon.height//2), text, font=fonts['font_md'], fill="black", anchor='mm')
  return icon


def get_cloud_cover_icon(cloud_cover: float, images: Icons, fonts: Fonts, config: SectionProxy) -> Image.Image:
  icon_index = math.nan if math.isnan(cloud_cover) else round(cloud_cover)
  if (not math.isnan(icon_index) and 0 <= icon_index <= 9):
    return images['misc'][f'cloud_cover_{icon_index}']
  icon = images['misc']['cloud_cover_0'].copy()
  draw = ImageDraw.Draw(icon)
  text = "NaN" if math.isnan(icon_index) else str(icon_index)
  draw.text((icon.width//2, icon.height//2), text, font=fonts['font_md'], fill="black", anchor='mm')
  return icon


def utc_datetime_string_to_local_datetime(date_string: str) -> Datetime:
  return parse(date_string).replace(tzinfo=ZoneInfo('UTC')).astimezone(tz=None)


def get_weather_warning_level(temperature: float, time: Datetime, config: SectionProxy) -> WeatherWarning:
  if temperature >= config.getint('EXTREME_HIGH_TEMPERATURE_WARNING_THRESHOLD'):
    return WeatherWarning.CRITICAL

  if temperature >= config.getint('HIGH_TEMPERATURE_WARNING_THRESHOLD'):
    return WeatherWarning.WARNING

  if temperature <= config.getint('EXTREME_LOW_TEMPERATURE_WARNING_THRESHOLD'):
    return WeatherWarning.CRITICAL

  if temperature <= config.getint('LOW_TEMPERATURE_WARNING_THRESHOLD'):
    return WeatherWarning.WARNING

  if temperature >= config.getint('TROPICAL_NIGHT_TEMPERATURE_WARNING_THRESHOLD') and (time.hour > 21 or time.hour < 8):
    return WeatherWarning.WARNING

  return WeatherWarning.NONE


def get_config_override_position(config: SectionProxy) -> Position:
  latitude = config.get('OVERRIDE_LATITUDE')
  longitude = config.get('OVERRIDE_LONGITUDE')
  return (latitude, longitude)


def is_supported_epd(epd_model: str) -> bool:
  return epd_model in SUPPORTED_EPD_MODELS


def roundToString(value: float, decimals: Optional[int] = None) -> str:
  if (math.isnan(value)):
    return NAN_SYMBOL
  return str(round(value, decimals))


def get_next_forecast_start_timestamp() -> Datetime:
  now = datetime.today()
  new_hour = ((now.hour-3)//6 + 1) * 6 + 3
  new_time = (now + timedelta(hours=new_hour - now.hour)).replace(minute=0, second=0, microsecond=0).astimezone(tz=None)
  return new_time
