from PIL import Image, ImageChops
from type_alias import Rect

# Area x and width are aligned to this so every bit depth packs whole words per row (1 bpp needs 16 px).
# Must match AREA_ALIGN in clib78/src/draw_image.h.
AREA_ALIGN = 16

# Above this share of the panel, one whole-panel update is cheaper than several area waveforms
FULL_PANEL_AREA_RATIO = 0.5


def get_changed_rects(previous: Image.Image, current: Image.Image, panel_rects: list[Rect]) -> list[Rect]:
  '''Bounding boxes of the changed pixels, one per panel rectangle plus one for changes outside all of them.
  Per-panel boxes keep e.g. a clock change and an observation change from merging into one big box.'''
  diff = ImageChops.difference(previous, current)
  rects: list[Rect] = []
  for (x, y, w, h) in panel_rects:
    bbox = diff.crop((x, y, x + w, y + h)).getbbox()
    if bbox is not None:
      rects.append((x + bbox[0], y + bbox[1], bbox[2] - bbox[0], bbox[3] - bbox[1]))
  # Changes outside the panels, e.g. borders
  for (x, y, w, h) in panel_rects:
    diff.paste(0, (x, y, x + w, y + h))
  bbox = diff.getbbox()
  if bbox is not None:
    rects.append((bbox[0], bbox[1], bbox[2] - bbox[0], bbox[3] - bbox[1]))
  return rects


def transform_rect(rect: Rect, size: tuple[int, int], mirror_horizontal: bool, rotate_180: bool) -> Rect:
  '''Maps a rectangle through the same mirror and rotation that are applied to the image before it is sent to the panel.'''
  (x, y, w, h) = rect
  if mirror_horizontal:
    x = size[0] - x - w
  if rotate_180:
    x = size[0] - x - w
    y = size[1] - y - h
  return (x, y, w, h)


def align_rect(rect: Rect, size: tuple[int, int], align: int = AREA_ALIGN) -> Rect:
  '''Widens x and width outwards to multiples of align, clamped to the panel. The panel width must be a multiple of align.'''
  (x, y, w, h) = rect
  left = x - x % align
  right = min(-(-(x + w) // align) * align, size[0])
  top = max(y, 0)
  bottom = min(y + h, size[1])
  return (left, top, right - left, bottom - top)


def _overlaps(a: Rect, b: Rect) -> bool:
  return a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and a[1] < b[1] + b[3] and b[1] < a[1] + a[3]


def _union(a: Rect, b: Rect) -> Rect:
  left = min(a[0], b[0])
  top = min(a[1], b[1])
  right = max(a[0] + a[2], b[0] + b[2])
  bottom = max(a[1] + a[3], b[1] + b[3])
  return (left, top, right - left, bottom - top)


def merge_overlapping(rects: list[Rect]) -> list[Rect]:
  '''Replaces overlapping rectangles with their union until none overlap, so no pixel gets two waveforms.'''
  merged = list(rects)
  changed = True
  while changed:
    changed = False
    for i in range(len(merged)):
      for j in range(i + 1, len(merged)):
        if _overlaps(merged[i], merged[j]):
          merged[i] = _union(merged[i], merged[j])
          del merged[j]
          changed = True
          break
      if changed:
        break
  return merged


def get_update_rects(previous: Image.Image, current: Image.Image, panel_rects: list[Rect], mirror_horizontal: bool, rotate_180: bool) -> list[Rect]:
  '''Areas to update, in panel coordinates, aligned for the C library. Empty when nothing changed. Falls back to the whole panel when the areas cover most of it.
  previous and current are the frames before mirroring and rotation.'''
  size = current.size
  rects = [align_rect(transform_rect(r, size, mirror_horizontal, rotate_180), size) for r in get_changed_rects(previous, current, panel_rects)]
  rects = merge_overlapping(rects)
  if sum(w * h for (_, _, w, h) in rects) > FULL_PANEL_AREA_RATIO * size[0] * size[1]:
    return [(0, 0, size[0], size[1])]
  return sorted(rects, key=lambda r: (r[1], r[0]))
