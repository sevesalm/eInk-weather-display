from PIL import Image, ImageDraw
from celestial import get_moon_phase, get_sunrise_sunset, get_moon_phase_chr
import logging
import utils

def parse_sunrise_sunset_time(val):
  return val.astimezone(tz=None).strftime('%-H:%M')

def get_celestial_panel(position, images, fonts, config):
  logger = logging.getLogger(__name__)
  logger.info('Generating celestial panel')
  x_size = 400
  y_size = 450 
  image = Image.new('L', (x_size, y_size), 0xff) 
  draw = ImageDraw.Draw(image)

  utils.draw_title(draw, fonts['font_sm'], 'SKY')
  
  # Icons
  (sunrise, sunset) = get_sunrise_sunset(position)
  image.paste(images['misc']['sunrise'], (x_size//4 - images['misc']['sunrise'].width//2, y_size - 200 ))
  image.paste(images['misc']['sunset'], (3*x_size//4  - images['misc']['sunset'].width//2, y_size - 200 ))

  data_y_base = y_size - 20

  # Times
  draw.text((x_size//4, data_y_base), parse_sunrise_sunset_time(sunrise), font = fonts['font_sm'], fill = 0, anchor = 'ms')
  draw.text((3*x_size//4, data_y_base), parse_sunrise_sunset_time(sunset), font = fonts['font_sm'], fill = 0, anchor = 'ms')

  (moon_phase, percent) = get_moon_phase()
  moon_font_chr = get_moon_phase_chr(moon_phase)
  font_moon = fonts['font_misc_md']
  draw.text((3*x_size//4, 20), moon_font_chr, font=font_moon, fill=0, anchor="ma")
  ascent, descent = font_moon.getmetrics()
  utils.draw_quantity(draw, (3*x_size//4, 20 + ascent + descent + 70), str(round(percent)), '%', fonts)

  # Borders
  if (config.getboolean('DRAW_PANEL_BORDERS')):
    draw.polygon([(0, 0), (x_size-1, 0), (x_size-1, y_size-1), (0, y_size-1), (0, 0)])
    
  return image 
