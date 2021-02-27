from PIL import Image, ImageDraw
from celestial import get_moon_phase, get_sunrise_sunset, map_moon_phase_to_icon

def parse_sunrise_sunset_time(val):
  return val.astimezone(tz=None).strftime('%H:%M')

def get_sunrise_sunset_panel(position, misc_images, fonts, config):
  (sunrise, sunset) = get_sunrise_sunset(position)
  x_size = 140
  y_size = 70 
  image = Image.new('L', (x_size, y_size), 0xff) 
  draw = ImageDraw.Draw(image)
  
  # Icons
  image.paste(misc_images['sunrise'], (int(x_size/4 - misc_images['sunrise'].width/2), 0))
  image.paste(misc_images['sunset'], (int(3*x_size/4  - misc_images['sunset'].width/2), 0))

  # Times
  draw.text((x_size/4, y_size-5), parse_sunrise_sunset_time(sunrise), font = fonts['font_sm'], fill = 0, anchor = 'md')
  draw.text((3*x_size/4, y_size-5), parse_sunrise_sunset_time(sunset), font = fonts['font_sm'], fill = 0, anchor = 'md')

  # Borders
  if (config['DRAW_PANEL_BORDERS']):
    draw.polygon([(0, 0), (x_size-1, 0), (x_size-1, y_size-1), (0, y_size-1), (0, 0)])
  return image

def get_moon_phase_panel(fonts, config):
  x_size = 70
  y_size = 70

  (moon_phase, percent) = get_moon_phase()
  icon = map_moon_phase_to_icon(moon_phase)
  image = Image.new('L', (x_size, y_size), 0xff)
  draw = ImageDraw.Draw(image)
  draw.text((x_size/2, 0), icon, font = fonts['font_weather_m'], fill = 0, anchor = 'mt') 
  draw.text((x_size/2, y_size - 5), f'{round(percent)} %', font = fonts['font_sm'], fill = 0, anchor = 'md') 

  # Borders
  if (config['DRAW_PANEL_BORDERS']):
    draw.polygon([(0, 0), (x_size-1, 0), (x_size-1, y_size-1), (0, y_size-1), (0, 0)])
    
  return image 
