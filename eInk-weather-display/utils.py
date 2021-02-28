def draw_quantity(draw, mid_point, value, unit, fonts, font='font_sm'):
  (x, y) = mid_point
  draw.text((x - 3, y), value, font = fonts[font], fill = 0, anchor = 'rm')
  draw.text((x + 3, y), unit, font = fonts[font], fill = 0, anchor = 'lm')