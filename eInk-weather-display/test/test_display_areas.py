import unittest
from PIL import Image, ImageDraw
from display_areas import AREA_ALIGN, align_rect, get_changed_rects, get_update_rects, merge_overlapping, transform_rect

SIZE = (1872, 1404)
# Similar to the real layout: two panels on the left, one on the right and one across the bottom
PANELS = [(0, 0, 800, 900), (800, 0, 812, 900), (1612, 0, 260, 400), (0, 904, 1872, 500)]


def blank() -> Image.Image:
  return Image.new('L', SIZE, 0xff)


def with_pixels(image: Image.Image, *points: tuple[int, int]) -> Image.Image:
  result = image.copy()
  for point in points:
    result.putpixel(point, 0)
  return result


class TestDisplayAreas(unittest.TestCase):
  def test_unchanged_image_has_no_areas(self):
    image = with_pixels(blank(), (100, 100))
    self.assertEqual(get_update_rects(image, image.copy(), PANELS, False, False), [])

  def test_single_pixel_is_aligned(self):
    rects = get_update_rects(blank(), with_pixels(blank(), (1700, 50)), PANELS, False, False)
    self.assertEqual(rects, [(1696, 50, 16, 1)])

  def test_changes_in_two_panels_stay_separate(self):
    current = with_pixels(blank(), (10, 10), (1700, 50))
    self.assertEqual(get_changed_rects(blank(), current, PANELS), [(10, 10, 1, 1), (1700, 50, 1, 1)])

  def test_box_is_limited_to_panel(self):
    current = blank()
    ImageDraw.Draw(current).text((1650, 100), '12:34', fill=0)
    [(x, y, w, h)] = get_changed_rects(blank(), current, PANELS)
    self.assertTrue(x >= 1612 and y >= 0 and x + w <= 1872 and y + h <= 400)

  def test_change_outside_panels_is_found(self):
    # Row 902 is in the gap between the top panels and the bottom panel
    self.assertEqual(get_changed_rects(blank(), with_pixels(blank(), (500, 902)), PANELS), [(500, 902, 1, 1)])

  def test_mirror(self):
    self.assertEqual(transform_rect((10, 20, 30, 40), SIZE, True, False), (1872 - 40, 20, 30, 40))

  def test_rotate(self):
    self.assertEqual(transform_rect((10, 20, 30, 40), SIZE, False, True), (1872 - 40, 1404 - 60, 30, 40))

  def test_mirror_and_rotate_flip_vertically(self):
    self.assertEqual(transform_rect((10, 20, 30, 40), SIZE, True, True), (10, 1404 - 60, 30, 40))

  def test_transformed_rect_matches_transformed_image(self):
    current = with_pixels(blank(), (1700, 50), (1710, 60))
    [rect] = get_changed_rects(blank(), current, PANELS)
    for (mirror, rotate) in [(True, False), (False, True), (True, True)]:
      transformed = current.transpose(Image.Transpose.FLIP_LEFT_RIGHT) if mirror else current
      transformed = transformed.rotate(180 if rotate else 0)
      bbox = Image.eval(transformed, lambda v: 255 - v).getbbox()
      assert bbox is not None
      self.assertEqual(transform_rect(rect, SIZE, mirror, rotate), (bbox[0], bbox[1], bbox[2] - bbox[0], bbox[3] - bbox[1]))

  def test_align_widens_outwards(self):
    self.assertEqual(align_rect((17, 5, 16, 3), SIZE), (16, 5, 32, 3))
    self.assertEqual(align_rect((32, 5, 16, 3), SIZE), (32, 5, 16, 3))

  def test_align_clamps_to_panel(self):
    self.assertEqual(align_rect((1860, 1400, 12, 10), SIZE), (1856, 1400, 16, 4))

  def test_aligned_rects(self):
    current = with_pixels(blank(), (3, 3), (1001, 500), (1871, 1403))
    for (mirror, rotate) in [(False, False), (True, False), (False, True), (True, True)]:
      for (x, y, w, h) in get_update_rects(blank(), current, PANELS, mirror, rotate):
        self.assertEqual(x % AREA_ALIGN, 0)
        self.assertEqual(w % AREA_ALIGN, 0)
        self.assertTrue(x + w <= SIZE[0] and y + h <= SIZE[1])

  def test_merge_overlapping(self):
    self.assertEqual(merge_overlapping([(0, 0, 16, 16), (8, 8, 16, 16), (100, 100, 16, 16)]), [(0, 0, 24, 24), (100, 100, 16, 16)])
    # Touching rectangles don't overlap
    self.assertEqual(merge_overlapping([(0, 0, 16, 16), (16, 0, 16, 16)]), [(0, 0, 16, 16), (16, 0, 16, 16)])

  def test_merge_is_transitive(self):
    self.assertEqual(merge_overlapping([(0, 0, 16, 16), (40, 0, 16, 16), (10, 0, 40, 16)]), [(0, 0, 56, 16)])

  def test_large_change_falls_back_to_whole_panel(self):
    current = blank()
    ImageDraw.Draw(current).rectangle((0, 0, 1871, 900), fill=0)
    self.assertEqual(get_update_rects(blank(), current, PANELS, False, False), [(0, 0, 1872, 1404)])


if __name__ == '__main__':
  unittest.main()
