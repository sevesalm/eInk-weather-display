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

ApiData = Mapping[str, Mapping[str, float]]

WeatherData = tuple[ApiData, tuple[str, str], str, str]


class SingleSensorData(TypedDict):
  temperature: float
  humidity: float
  battery: float
  rssi: float


SensorData = Mapping[str, SingleSensorData]
