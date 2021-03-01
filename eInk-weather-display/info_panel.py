import time
from PIL import Image, ImageDraw
import logging

def get_info_panel(fonts, config):
  logger = logging.getLogger(__name__)
  logger.info('Generating info panel')
  x_size = 200
  y_size = 18
  image = Image.new('L', (x_size, y_size), 0xff)
  draw = ImageDraw.Draw(image)
  draw.text((195, 0), f'{config.get("FMI_LOCATION")} - {time.strftime("%H:%M:%S")}', font = fonts['font_xs'], fill = 0, anchor = 'ra')

  # Borders
  if (config.getboolean('DRAW_PANEL_BORDERS')):
    draw.polygon([(0, 0), (x_size-1, 0), (x_size-1, y_size-1), (0, y_size-1), (0, 0)])
    
  return image