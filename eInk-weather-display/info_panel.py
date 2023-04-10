import time
from PIL import Image, ImageDraw
import logging
from configparser import SectionProxy
from type_alias import Fonts


def get_info_panel(fonts: Fonts, config: SectionProxy) -> Image.Image:
  logger = logging.getLogger(__name__)
  logger.info('Generating info panel')
  x_size = 260
  y_size = 400
  image = Image.new('L', (x_size, y_size), 0xff)
  draw = ImageDraw.Draw(image)

  draw.text((x_size//2, 20), f'{time.strftime("%-H:%M")}', fill="black", font=fonts['font_md'], anchor='mt')
  draw.text((x_size//2, 180), f'{time.strftime("%-d.%-m.%Y")}', fill="black", font=fonts['font_sm'], anchor='ms')

  if (config.getboolean('DEV_MODE')):
    draw.text((x_size//2, 250), '(DEV MODE)', fill="black", font=fonts['font_xxs'], anchor='ms')

  # Borders
  if (config.getboolean('DRAW_PANEL_BORDERS')):
    draw.polygon([(0, 0), (x_size-1, 0), (x_size-1, y_size-1), (0, y_size-1), (0, 0)])

  return image
