import sys
import ctypes
from PIL import ImageFont

def draw_quantity(draw, mid_point, value, unit, fonts, font='font_sm', font_unit='font_xs'):
  (x, y) = mid_point
  draw.text((x - 7, y), value, font = fonts[font], fill = 0, anchor = 'rs')
  draw.text((x + 7, y), unit, font = fonts[font_unit], fill = 0, anchor = 'ls')

def check_python_version():
  major = sys.version_info[0]
  minor = sys.version_info[1]
  if major < 3 or minor < 7:
    raise Exception('Python 3.7 or newer required')

# Converts a 8-bit image into a packed 2-bit image which can be fed to EPD
def from_8bit_to_2bit(image):
  if(image.mode != 'L'):
    raise Exception('Image mode must be \'L\'')
  if(image.width % 4 != 0):
    raise Exception('Image width % 4 must be 0')
  
  image_bytes = image.tobytes()
  result = bytearray()
  for y in range(image.height):
    for x in range(image.width // 4):
      px0 = (image_bytes[y*image.width + x*4 + 0] & (0x3 << 6)) >> 0
      px1 = (image_bytes[y*image.width + x*4 + 1] & (0x3 << 6)) >> 2
      px2 = (image_bytes[y*image.width + x*4 + 2] & (0x3 << 6)) >> 4
      px3 = (image_bytes[y*image.width + x*4 + 3] & (0x3 << 6)) >> 6

      new_px = px0 | px1 | px2 | px3
      result.append(new_px)
  return bytes(result)

def get_epd_data(config):
  if(config.get('EPD_MODEL') == '7.8'):
    if (config.getboolean('FILE_OUTPUT')):
      return (None, (1872, 1404))
    else:
      return (ctypes.CDLL("lib/epd78.so"), (1872, 1404))
  else:
    raise Exception(f'Unsupported model: {config.get("EPD_MODEL")}')


def get_fonts(config):
  if(config.get('EPD_MODEL') == '7.8'):
    font_mult = 4
  else:
    raise Exception(f'Unsupported model: {config.get("EPD_MODEL")}')

  return {
    'font_lg': ImageFont.truetype('fonts/regular.woff', font_mult * 42),
    'font_md': ImageFont.truetype('fonts/regular.woff', font_mult * 32),
    'font_sm': ImageFont.truetype('fonts/regular.woff', font_mult * 18),
    'font_sm_bold': ImageFont.truetype('fonts/bold.woff', font_mult * 18),
    'font_xs': ImageFont.truetype('fonts/regular.woff', font_mult * 14),
    'font_xxs': ImageFont.truetype('fonts/regular.woff', font_mult * 8)
  }

def draw_title(draw, title_size, title, fonts):
  draw.rectangle([(0, 0), (title_size[0], title_size[1])], fill=0x00)
  draw.text((title_size[0]//2, title_size[1]//2), title, fill="white", font=fonts['font_sm'], anchor='mm')
