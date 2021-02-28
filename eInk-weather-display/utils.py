import sys

def draw_quantity(draw, mid_point, value, unit, fonts, font='font_sm'):
  (x, y) = mid_point
  draw.text((x - 3, y), value, font = fonts[font], fill = 0, anchor = 'rm')
  draw.text((x + 3, y), unit, font = fonts[font], fill = 0, anchor = 'lm')

def check_python_version():
  major = sys.version_info[0]
  minor = sys.version_info[1]
  if major < 3 or minor < 7:
    raise Exception('Python 3.7 or newer required')