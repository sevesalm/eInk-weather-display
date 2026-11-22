import unittest
from icons import FORECAST_ICON_SIZE, MISC_ICON_HEIGHTS, MISC_ICON_WIDTHS, OBSERVATION_ICON_SIZE, SVG_ICON_DIR, get_weather_images, render_icon
from type_alias import Icons


class TestIcons(unittest.TestCase):
  images: Icons

  @classmethod
  def setUpClass(cls) -> None:
    # Fails if any mapped icon is missing or can't be rendered
    cls.images = get_weather_images()

  def test_every_svg_renders(self) -> None:
    for path in sorted(SVG_ICON_DIR.glob('*.svg')):
      with self.subTest(icon=path.stem):
        icon = render_icon(path.stem, width=50)
        self.assertEqual(icon.mode, 'RGBA')
        self.assertEqual(icon.width, 50)

  def test_glyph_background_is_transparent(self) -> None:
    # The SVGs set a white background for editing, which must not end up in the rendered icon
    icon = render_icon('clear', width=100)
    self.assertEqual(icon.getpixel((0, 0)), (0, 0, 0, 0))

  def test_weather_icons_are_composited_on_background(self) -> None:
    clear = self.images['weather_symbol_3'][1]
    # Opaque background corner-to-corner inside the rounded rectangle, gray at night and lighter during the day
    day_pixel = clear['day'].getpixel((FORECAST_ICON_SIZE // 2, 5))
    night_pixel = clear['night'].getpixel((FORECAST_ICON_SIZE // 2, 5))
    assert isinstance(day_pixel, tuple) and isinstance(night_pixel, tuple)
    self.assertEqual(day_pixel[1], 255)
    self.assertEqual(night_pixel[1], 255)
    self.assertGreater(day_pixel[0], night_pixel[0])
    self.assertLess(night_pixel[0], 255)

  def test_icon_sizes(self) -> None:
    groups = [
      ('observation', self.images['observation'], OBSERVATION_ICON_SIZE),
      ('observation_cloud_cover', self.images['observation_cloud_cover'], OBSERVATION_ICON_SIZE),
      ('weather_symbol_3', self.images['weather_symbol_3'], FORECAST_ICON_SIZE),
      ('smart_symbol', self.images['smart_symbol'], FORECAST_ICON_SIZE),
    ]
    for group, icon_sets, size in groups:
      for key, icon_set in icon_sets.items():
        for variant, icon in [('day', icon_set['day']), ('night', icon_set['night'])]:
          with self.subTest(group=group, key=key, variant=variant):
            self.assertEqual(icon.mode, 'LA')
            self.assertEqual(icon.width, size)
    misc = self.images['misc']
    for name, width in MISC_ICON_WIDTHS.items():
      self.assertEqual(misc[name].width, width, name)
    for name, height in MISC_ICON_HEIGHTS.items():
      self.assertEqual(misc[name].height, height, name)
