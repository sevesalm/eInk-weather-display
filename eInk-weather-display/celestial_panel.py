from PIL import Image, ImageDraw
from celestial import get_moon_phase, get_sunrise_sunset, map_moon_phase_to_icon
import logging

def parse_sunrise_sunset_time(val):
  return val.astimezone(tz=None).strftime('%-H:%M')

def get_celestial_panel(position, misc_images, fonts, config):
  logger = logging.getLogger(__name__)
  logger.info('Generating celestial panel')
  x_size = 180
  y_size = 70 
  image = Image.new('L', (x_size, y_size), 0xff) 
  draw = ImageDraw.Draw(image)
  
  # Icons
  (sunrise, sunset) = get_sunrise_sunset(position)
  image.paste(misc_images['sunrise'], (int(x_size/6 - misc_images['sunrise'].width/2), 0))
  image.paste(misc_images['sunset'], (int(3*x_size/6  - misc_images['sunset'].width/2), 0))

  # Times
  draw.text((x_size/6, y_size-5), parse_sunrise_sunset_time(sunrise), font = fonts['font_sm'], fill = 0, anchor = 'md')
  draw.text((3*x_size/6, y_size-5), parse_sunrise_sunset_time(sunset), font = fonts['font_sm'], fill = 0, anchor = 'md')

  (moon_phase, percent) = get_moon_phase()
  icon = map_moon_phase_to_icon(moon_phase)
  draw.text((5*x_size/6, 0), icon, font = fonts['font_weather_m'], fill = 0, anchor = 'mt') 
  draw.text((5*x_size/6, y_size - 5), f'{round(percent)} %', font = fonts['font_sm'], fill = 0, anchor = 'md') 

  # Borders
  if (config.getboolean('DRAW_PANEL_BORDERS')):
    draw.polygon([(0, 0), (x_size-1, 0), (x_size-1, y_size-1), (0, y_size-1), (0, 0)])
    
  return image 
