import sys
import math
import resource
import ctypes
from PIL import ImageFont, ImageDraw, Image, features
from dateutil.parser import parse
from zoneinfo import ZoneInfo
from typing import Optional, Union
from type_alias import Datetime, Fonts, Icons, DayNightIcons, WeatherWarning, Position
from datetime import datetime, timedelta
import logging
from app_config import AppConfig
from paths import APP_DIR
import icons

NAN_SYMBOL = '?'
FULL_REFRESH_OFFSET_SECONDS = 5 * 60

TABULAR_NUMBERS_FEATURES = ["tnum"]  # OpenType feature for tabular numbers
RAQM_SUPPORTED = features.check_feature('raqm')


def get_features() -> Optional[list[str]]:
  '''OpenType features used when drawing text. Disabled when Raqm is missing because Pillow raises without it.'''
  return TABULAR_NUMBERS_FEATURES if RAQM_SUPPORTED else None


def draw_quantity(draw: ImageDraw.ImageDraw, mid_point: tuple[int, int], value: str, unit: str, fonts: Fonts, font: str = 'font_sm', font_unit: str = 'font_xs') -> None:
  (x, y) = mid_point
  offset = 7
  draw.text((x - offset, y), value, font=fonts[font], fill=0, anchor='rs', features=get_features())
  draw.text((x + offset, y), unit, font=fonts[font_unit], fill=0, anchor='ls')


def draw_time(draw: ImageDraw.ImageDraw, coordinate: tuple[int, int], minutes: str, hours: str, font: ImageFont.FreeTypeFont) -> None:
  offset = font.size//8
  text_features = get_features()
  draw.text(coordinate, ":", font=font, fill=0, anchor='mm')
  draw.text((coordinate[0]+offset, coordinate[1]), minutes, font=font, fill=0, anchor='lm', features=text_features)
  draw.text((coordinate[0]-offset, coordinate[1]), hours, font=font, fill=0, anchor='rm', features=text_features)


def check_raqm_support(logger: logging.Logger) -> None:
  '''Check if the Raqm support is enabled. Used to enable OpenType font features.'''
  if RAQM_SUPPORTED:
    logger.info("Raqm support detected")
  else:
    logger.warning('Raqm not supported')


def check_python_version() -> None:
  if sys.version_info < (3, 14):
    raise Exception('Python 3.14 or newer required')


def get_peak_memory_mb() -> float:
  '''Peak resident set size of the process in MiB. ru_maxrss is in bytes on macOS and in kilobytes on Linux.'''
  max_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
  return max_rss / (1024 * 1024) if sys.platform == 'darwin' else max_rss / 1024


def get_epd_data(config: AppConfig) -> tuple[Optional[ctypes.CDLL], tuple[int, int]]:
  if (config.dev_mode):
    return (None, (1872, 1404))
  epd_so = ctypes.CDLL(str(APP_DIR / 'lib' / 'epd78.so'))
  epd_so.draw_image_8bit_areas.restype = ctypes.c_int
  return (epd_so, (1872, 1404))


def get_fonts(config: AppConfig) -> Fonts:
  font_mult = 4
  font_dir = APP_DIR / 'fonts'

  return {
    'font_lg': ImageFont.truetype(font_dir / 'regular.woff', font_mult * 42),
    'font_md': ImageFont.truetype(font_dir / 'regular.woff', font_mult * 32),
    'font_sm': ImageFont.truetype(font_dir / 'regular.woff', font_mult * 18),
    'font_sm_bold': ImageFont.truetype(font_dir / 'bold.woff', font_mult * 18),
    'font_xs': ImageFont.truetype(font_dir / 'regular.woff', font_mult * 14),
    'font_xxs': ImageFont.truetype(font_dir / 'regular.woff', font_mult * 9),
    'font_misc_md': ImageFont.truetype(font_dir / 'misc.woff', font_mult * 32)
  }


def get_text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> tuple[float, float]:
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


def get_missing_weather_icon_icon(icon_index: Union[float, int], is_daylight: bool, size: int, images: Icons, fonts: Fonts, config: AppConfig) -> Image.Image:
  icon = icons.get_scaled_image(images['misc']['background_day'] if is_daylight else images['misc']['background_night'], size)
  draw = ImageDraw.Draw(icon)
  text = "NaN" if math.isnan(icon_index) else str(icon_index)
  draw.text((icon.width//2, icon.height//2), text, font=fonts['font_sm'], fill="black", anchor='mm', features=get_features())
  return icon


def get_cloud_cover_icon(cloud_cover: float, images: Icons, fonts: Fonts, config: AppConfig) -> Image.Image:
  icon_index = math.nan if math.isnan(cloud_cover) else round(cloud_cover)
  if (not math.isnan(icon_index) and 0 <= icon_index <= 9):
    return images['misc'][f'cloud_cover_{icon_index}']
  icon = images['misc']['cloud_cover_0'].copy()
  draw = ImageDraw.Draw(icon)
  text = "NaN" if math.isnan(icon_index) else str(icon_index)
  draw.text((icon.width//2, icon.height//2), text, font=fonts['font_xxs'], fill="black", anchor='mm', features=get_features())
  return icon


def utc_datetime_string_to_local_datetime(date_string: str) -> Datetime:
  date = parse(date_string)
  if date.tzinfo is None:
    date = date.replace(tzinfo=ZoneInfo('UTC'))
  return date.astimezone(tz=None)


def get_weather_warning_level(temperature: float, time: Datetime, config: AppConfig) -> WeatherWarning:
  if temperature >= config.extreme_high_temperature_warning_threshold:
    return WeatherWarning.CRITICAL

  if temperature >= config.high_temperature_warning_threshold:
    return WeatherWarning.WARNING

  if temperature <= config.extreme_low_temperature_warning_threshold:
    return WeatherWarning.CRITICAL

  if temperature <= config.low_temperature_warning_threshold:
    return WeatherWarning.WARNING

  if temperature >= config.tropical_night_temperature_warning_threshold and (time.hour > 21 or time.hour < 8):
    return WeatherWarning.WARNING

  return WeatherWarning.NONE


def get_config_override_position(config: AppConfig) -> Position:
  latitude = str(config.override_latitude)
  longitude = str(config.override_longitude)
  return (latitude, longitude)


def roundToString(value: float, decimals: Optional[int] = None) -> str:
  if (math.isnan(value)):
    return NAN_SYMBOL
  return str(round(value, decimals))


def get_next_forecast_start_timestamp() -> Datetime:
  now = datetime.today()
  new_hour = ((now.hour-3)//6 + 1) * 6 + 3
  new_time = (now + timedelta(hours=new_hour - now.hour)).replace(minute=0, second=0, microsecond=0).astimezone(tz=None)
  return new_time


def get_latest_full_refresh_slot(now: Datetime, interval: int) -> Datetime:
  '''Latest scheduled full refresh time at or before now. Slots are 5 minutes, 5 minutes + interval, ... after the start of each hour (interval in seconds).'''
  hour = now.replace(minute=0, second=0, microsecond=0)
  seconds = now.minute * 60 + now.second
  return hour + timedelta(seconds=seconds - (seconds - FULL_REFRESH_OFFSET_SECONDS) % interval)


def should_full_refresh(now: Datetime, last_full_refresh: Optional[Datetime], interval: int) -> bool:
  '''True when no full refresh has run since the latest slot, so a skipped slot is caught up on the next run.'''
  return last_full_refresh is None or last_full_refresh < get_latest_full_refresh_slot(now, interval)
