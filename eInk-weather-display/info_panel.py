import time
from PIL import Image, ImageDraw
import logging

def get_info_panel(fonts, config):
  logger = logging.getLogger(__name__)
  logger.info('Generating info panel')
  x_size = 270
  y_size = 200
  image = Image.new('L', (x_size, y_size), 0xff)
  draw = ImageDraw.Draw(image)
  
  draw.text((x_size - 20, 20), f'{time.strftime("%-H:%M")}', fill="black", font=fonts['font_md'], anchor='rt')
  draw.text((x_size - 20, y_size - 20), f'{time.strftime("%-d.%-m.%Y")}', fill="black", font=fonts['font_sm'], anchor='rs')

  # Borders
  if (config.getboolean('DRAW_PANEL_BORDERS')):
    draw.polygon([(0, 0), (x_size-1, 0), (x_size-1, y_size-1), (0, y_size-1), (0, 0)])
    
  return image