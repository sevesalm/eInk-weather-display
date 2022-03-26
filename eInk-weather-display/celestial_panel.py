from PIL import Image, ImageDraw
from celestial import get_moon_phase, get_moon_phase_chr, get_dusks_and_dawns
import logging
import utils
import icons
import datetime

def parse_sunrise_sunset_time(val):
  if(val == None):
    return 'N/A'
  return val.astimezone(tz=None).strftime('%-H:%M')

def parse_sunrise_sunset_hour_minute(val):
  return (val.astimezone(tz=None).strftime('%-H'), val.astimezone(tz=None).strftime('%M'))

def get_shade_color(shade):
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


def get_celestial_panel(position, images, fonts, config):
  logger = logging.getLogger(__name__)
  logger.info('Generating celestial panel')
  x_size = 400
  y_size = 600 
  image = Image.new('L', (x_size, y_size), 0xff) 
  draw = ImageDraw.Draw(image)

  utils.draw_title(draw, fonts['font_sm'], 'SKY')
  
  # Icons
  now = datetime.datetime.now().astimezone()
  dusks_and_dawns = get_dusks_and_dawns(position, now)

  tick_height = 50
  y_base = 80 + (9 - len(dusks_and_dawns["twilights"])) * tick_height//2
  x_base = 150
  tick_width = 20
  tick_gap = 20
  arrow_gap = 5
  arrow_width = 25

  y_position = y_base
  for shade, new_threshold in zip(dusks_and_dawns["twilights"], dusks_and_dawns["times"] + [None]):
    if (new_threshold != None):
      (hours, minutes) = parse_sunrise_sunset_hour_minute(new_threshold)
      draw.text((x_base - 60, y_position+tick_height), ":", font = fonts['font_xs'], fill = 0, anchor = 'mm')
      draw.text((x_base - 53, y_position+tick_height), minutes, font = fonts['font_xs'], fill = 0, anchor = 'lm')
      draw.text((x_base - 67 , y_position+tick_height), hours, font = fonts['font_xs'], fill = 0, anchor = 'rm')

      draw.rectangle([(x_base + 10, y_position + tick_height - 1), (x_base + 20, y_position + tick_height + 1)], "#000")
    color = get_shade_color(shade)
    draw.rectangle([(x_base + tick_gap, y_position), (x_base + tick_gap + tick_width, y_position + tick_height)], color)
    y_position += tick_height

  arrow_offset = y_base + dusks_and_dawns["now_index"] * tick_height + tick_height//2
  draw.polygon([(x_base + tick_gap + tick_width + arrow_gap + arrow_width, -10 + arrow_offset), (x_base + tick_gap + tick_width + arrow_gap, arrow_offset), (x_base + tick_gap + tick_width + arrow_gap + arrow_width, 10 + arrow_offset)], "#000")

  (moon_phase, percent) = get_moon_phase()
  moon_font_chr = get_moon_phase_chr(moon_phase)
  font_moon = fonts['font_misc_md']
  draw.text((3*x_size//4, 90), moon_font_chr, font=font_moon, fill=0, anchor="ma")
  ascent, descent = font_moon.getmetrics()
  utils.draw_quantity(draw, (3*x_size//4, 90 + ascent + descent + 70), str(round(percent)), '%', fonts)

  # Borders
  if (config.getboolean('DRAW_PANEL_BORDERS')):
    draw.polygon([(0, 0), (x_size-1, 0), (x_size-1, y_size-1), (0, y_size-1), (0, 0)])
    
  return image 
