import datetime
from PIL import Image, ImageFont
from typing import Mapping, TypedDict

Datetime = datetime.datetime

class DayNightIcons(TypedDict):
  day: Image.Image
  night: Image.Image

class Icons(TypedDict):
    observation: Mapping[int, DayNightIcons]
    forecast: Mapping[int, DayNightIcons]
    misc: Mapping[str, Image.Image]

Fonts = Mapping[str, ImageFont.FreeTypeFont]

Position = tuple[str, str]