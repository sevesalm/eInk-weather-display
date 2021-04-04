from PIL import Image, ImageDraw
from celestial import get_moon_phase, get_sunrise_sunset, get_moon_phase_icon
import logging
import utils

def parse_sunrise_sunset_time(val):
  return val.astimezone(tz=None).strftime('%-H:%M')

def get_celestial_panel(position, images, fonts, config):
  logger = logging.getLogger(__name__)
  logger.info('Generating celestial panel')
  x_size = 600
  y_size = 250 
  image = Image.new('L', (x_size, y_size), 0xff) 
  draw = ImageDraw.Draw(image)

  # utils.draw_title(draw, (120, 80), 'SPACE', fonts)
  
  # Icons
  (sunrise, sunset) = get_sunrise_sunset(position)
  image.paste(images['misc']['sunrise'], (x_size//6 - images['misc']['sunrise'].width//2, 0))
  image.paste(images['misc']['sunset'], (3*x_size//6  - images['misc']['sunset'].width//2, 0))

  data_y_base = y_size-20

  # Times
  draw.text((x_size//6, data_y_base), parse_sunrise_sunset_time(sunrise), font = fonts['font_sm'], fill = 0, anchor = 'ms')
  draw.text((3*x_size//6, data_y_base), parse_sunrise_sunset_time(sunset), font = fonts['font_sm'], fill = 0, anchor = 'ms')

  (moon_phase, percent) = get_moon_phase()
  moon_icon = get_moon_phase_icon(moon_phase, images)
  utils.draw_quantity(draw, (5*x_size//6, data_y_base), str(round(percent)), '%', fonts)
  image.paste(moon_icon, (5*x_size//6 - moon_icon.width//2, 0))

  # Borders
  if (config.getboolean('DRAW_PANEL_BORDERS')):
    draw.polygon([(0, 0), (x_size-1, 0), (x_size-1, y_size-1), (0, y_size-1), (0, 0)])
    
  return image 
