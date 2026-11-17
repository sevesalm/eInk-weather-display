from enum import Enum
import datetime
from PIL import Image, ImageFont
from typing import Mapping, TypedDict

Datetime = datetime.datetime


class ObservationDataItem(TypedDict):
  t2m: float
  rh: float
  p_sea: float
  ws_10min: float
  wd_10min: float
  wg_10min: float
  n_man: float
  wawa: float


class ForecastDataItem(TypedDict):
  Temperature: float
  WindSpeedMS: float
  WindDirection: float
  TotalCloudCover: float
  WeatherSymbol3: float
  SmartSymbol: float


class RadiationDataItem(TypedDict):
  dir_1min: float


class DayNightIcons(TypedDict):
  day: Image.Image
  night: Image.Image


class Icons(TypedDict):
    observation: Mapping[int, DayNightIcons]
    weather_symbol_3: Mapping[int, DayNightIcons]
    smart_symbol: Mapping[int, DayNightIcons]
    misc: Mapping[str, Image.Image]


Fonts = Mapping[str, ImageFont.FreeTypeFont]

Position = tuple[str, str]

ObservationData = tuple[Mapping[str, ObservationDataItem], tuple[str, str], str, str]
ForecastData = tuple[Mapping[str, ForecastDataItem], tuple[str, str], str, str]
RadiationData = Mapping[str, RadiationDataItem]


class WeatherWarning(Enum):
  NONE = 0
  WARNING = 1
  CRITICAL = 2
