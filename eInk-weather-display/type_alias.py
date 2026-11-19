from enum import Enum
import datetime
from PIL import Image, ImageFont
from typing import Mapping, TypedDict
from pydantic import ConfigDict, with_config

# Weather data items are validated with pydantic (see validate_data.py): no missing or extra parameters, values must be numbers (NaN allowed)
WEATHER_DATA_CONFIG = ConfigDict(extra='forbid', strict=True)

Datetime = datetime.datetime


@with_config(WEATHER_DATA_CONFIG)
class ObservationDataItem(TypedDict):
  t2m: float
  rh: float
  p_sea: float
  ws_10min: float
  wd_10min: float
  wg_10min: float
  n_man: float
  wawa: float


@with_config(WEATHER_DATA_CONFIG)
class ForecastDataItem(TypedDict):
  Temperature: float
  WindSpeedMS: float
  WindDirection: float
  TotalCloudCover: float
  WeatherSymbol3: float
  SmartSymbol: float


@with_config(WEATHER_DATA_CONFIG)
class RadiationDataItem(TypedDict):
  dir_1min: float


class DayNightIcons(TypedDict):
  day: Image.Image
  night: Image.Image


class Icons(TypedDict):
    observation: Mapping[int, DayNightIcons]
    observation_cloud_cover: Mapping[int, DayNightIcons]
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
