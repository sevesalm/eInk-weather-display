from PIL import Image, ImageDraw
from celestial import get_moon_phase, get_moon_phase_chr, get_dusks_and_dawns, get_daytime_length, Twilight
import logging
import utils
import icons
import datetime
from configparser import SectionProxy
from type_alias import Fonts, Position, Datetime, Icons


def parse_sunrise_sunset_time(datetime: Datetime) -> str:
  if (datetime is None):
    return 'N/A'
  return datetime.astimezone(tz=None).strftime('%-H:%M')


def parse_sunrise_sunset_hour_minute(datetime: Datetime) -> tuple[str, str]:
  return (datetime.astimezone(tz=None).strftime('%-H'), datetime.astimezone(tz=None).strftime('%M'))


def get_shade_color(shade: int) -> str:
  if (shade == 0):
    return "#eee"
  elif (shade == 1):
    return "#ccc"
  elif (shade == 2):
    return "#888"
  elif (shade == 3):
    return "#444"
  elif (shade == 4):
    return "#000"
  raise Exception('Unsupported shade')


def get_celestial_panel(position: Position, position_name: str, fonts: Fonts, images: Icons, config: SectionProxy) -> Image.Image:
  logger = logging.getLogger(__name__)
  logger.info('Generating celestial panel')
  x_size = 500
  y_size = 600
  image = Image.new('L', (x_size, y_size), 0xff)
  draw = ImageDraw.Draw(image)

  utils.draw_title(draw, fonts['font_sm'], 'SKY', position_name, fonts['font_xxs'])

  # Icons
  now = datetime.datetime.now().astimezone()
  dusks_and_dawns = get_dusks_and_dawns(position, now)

  tick_height_map = [80, 45, 45, 45, 45]
  tick_heights = [tick_height_map[x] for x in dusks_and_dawns["twilights"]]
  tick_height_total = sum(tick_heights)
  y_base = 100 + sum(tick_height_map[1:]) + tick_height_map[0]//2 - tick_height_total//2
  x_base = 150
  tick_width = 20
  tick_gap = 20
  arrow_gap = 5
  arrow_width = 25

  y_position = y_base
  for shade, tick_height in zip(dusks_and_dawns["twilights"], tick_heights):
    color = get_shade_color(shade)
    draw.rectangle(((x_base + tick_gap, y_position), (x_base + tick_gap + tick_width, y_position + tick_height)), color)
    y_position += tick_height

  y_position = y_base
  for new_threshold, tick_height, prev_shade, next_shade in zip(dusks_and_dawns["times"], tick_heights, dusks_and_dawns["twilights"][:-1], dusks_and_dawns["twilights"][1:]):
    (hours, minutes) = parse_sunrise_sunset_hour_minute(new_threshold)
    font = fonts['font_xs'] if Twilight.DAYTIME in [prev_shade, next_shade] else fonts['font_xxs']
    draw.text((x_base - 69, y_position+tick_height), ":", font=font, fill=0, anchor='mm')
    draw.text((x_base - 62, y_position+tick_height), minutes, font=font, fill=0, anchor='lm')
    draw.text((x_base - 76, y_position+tick_height), hours, font=font, fill=0, anchor='rm')
    draw.rectangle(((x_base + 10, y_position + tick_height - 1), (x_base + 20, y_position + tick_height + 1)), "#000")
    y_position += tick_height

  # Current twilight
  current_twilight_index = int(dusks_and_dawns['current_twilight'])
  current_twilight_fraction = dusks_and_dawns['current_twilight'] % 1
  arrow_offset = y_base + sum(tick_heights[:current_twilight_index]) + tick_heights[current_twilight_index] * current_twilight_fraction
  # Arrow on the right side
  # draw.polygon([(x_base + tick_gap + tick_width + arrow_gap + arrow_width, -10 + arrow_offset), (x_base + tick_gap + tick_width + arrow_gap, arrow_offset), (x_base + tick_gap + tick_width + arrow_gap + arrow_width, 10 + arrow_offset)], "#000")
  # Arrow on the left side
  draw.polygon([(x_base + tick_gap - arrow_gap - arrow_width, -10 + arrow_offset), (x_base + tick_gap - arrow_gap, arrow_offset), (x_base + tick_gap - arrow_gap - arrow_width, 10 + arrow_offset)], "#000")

  # Moon phase
  (moon_phase, _) = get_moon_phase()
  moon_font_chr = get_moon_phase_chr(moon_phase)
  font_moon = fonts['font_misc_md']
  draw.text((3*x_size//4, 90), moon_font_chr, font=font_moon, fill=0, anchor="ma")
  # ascent, descent = font_moon.getmetrics()
  # utils.draw_quantity(draw, (3*x_size//4, 90 + ascent + descent + 70), str(round(percent)), '%', fonts)

  # Daytime length
  daytime_length = get_daytime_length(dusks_and_dawns)
  if (daytime_length is not None):
    daytime_index = dusks_and_dawns["twilights"].index(Twilight.DAYTIME)
    length_y_position = y_base + sum(tick_heights[0:daytime_index]) + tick_heights[daytime_index]//2
    minutes = str((daytime_length.seconds//60) % 60) + ' min'
    hours = str(daytime_length.seconds//3600) + ' h'
    text = ' '.join([hours, minutes])
    draw.text((x_base + tick_gap + tick_width + 90, length_y_position), text, font=fonts['font_xs'], fill=0, anchor='lm')
    # Sunrise icon
    sunrise_icon = icons.get_scaled_image_by_height(images['misc']['sunrise'], 50)
    image.paste(sunrise_icon, (x_base + tick_gap + tick_width + 10, length_y_position - sunrise_icon.height//2), sunrise_icon)

  # Borders
  if (config.getboolean('DRAW_PANEL_BORDERS')):
    draw.polygon([(0, 0), (x_size-1, 0), (x_size-1, y_size-1), (0, y_size-1), (0, 0)])

  return image
