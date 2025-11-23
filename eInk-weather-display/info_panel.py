import time
from PIL import Image, ImageDraw
import logging
import utils
from configparser import SectionProxy
from type_alias import Fonts


def get_info_panel(fonts: Fonts, config: SectionProxy) -> Image.Image:
  logger = logging.getLogger(__name__)
  logger.info('Generating info panel')
  x_size = 260
  y_size = 400
  image = Image.new('L', (x_size, y_size), 0xff)
  draw = ImageDraw.Draw(image)
  utils.draw_title(draw, fonts['font_sm'], 'INFO', None, fonts['font_xxs'])

  draw.text((x_size//2, 90), f'{time.strftime("%-H:%M")}', fill="black", font=fonts['font_md'], anchor='mt')
  draw.text((x_size//2, 250), f'{time.strftime("%a %-d.%-m.")}', fill="black", font=fonts['font_sm'], anchor='ms')
  draw.text((x_size//2, 300), f'{time.strftime("Week %V")}', fill="black", font=fonts['font_xs'], anchor='ms')
  draw.text((x_size//2, 350), f'{time.strftime("%Y")}', fill="black", font=fonts['font_xs'], anchor='ms')

  if (config.getboolean('DEV_MODE')):
    draw.text((x_size//2, 400), '(DEV MODE)', fill="black", font=fonts['font_xxs'], anchor='ms')

  # Borders
  if (config.getboolean('DRAW_PANEL_BORDERS')):
    draw.polygon([(0, 0), (x_size-1, 0), (x_size-1, y_size-1), (0, y_size-1), (0, 0)])

  return image
