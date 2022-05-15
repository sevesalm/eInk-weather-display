import random
import math
from PIL import Image, ImageDraw
from celestial import get_is_daylight
import logging
import utils
import icons
from configparser import SectionProxy
from type_alias import Fonts, Icons, WeatherData


def get_forecasts_panel(forecast_data: WeatherData, images: Icons, fonts: Fonts, config: SectionProxy) -> tuple[Image.Image, tuple[str, str]]:
  logger = logging.getLogger(__name__)
  logger.info('Generating forecast panel')
  icon_width = config.getint('ICON_WIDTH')
  x_size = 1872
  y_size = 800
  (forecasts, position, position_name) = forecast_data
  count = len(forecasts.keys())
  logger.info('Received data: %s', repr(forecasts))

  dates = sorted(forecasts.keys())
  image = Image.new('L', (x_size, y_size), 0xff)
  draw = ImageDraw.Draw(image)

  utils.draw_title(draw, fonts['font_sm'], 'FORECAST', position_name, fonts['font_xxs'])

  data_y_base = 100

  for date, i in zip(dates, range(len(dates))):
    is_daylight = get_is_daylight(position, date)
    data = forecasts[date]
    date_local = utils.utc_datetime_string_to_local_datetime(date)
    date_formatted = date_local.strftime('%-H:%M')
    x_step = x_size//count
    x_base = x_step//2

    # Time
    draw.text((x_base + i*x_step, data_y_base + 10), date_formatted, font=(fonts['font_sm'] if date_formatted != "15:00" else fonts['font_sm_bold']), fill=0, anchor='mt')

    # Weather icon
    icon_position = (x_base + i*x_step - config.getint('ICON_WIDTH')//2, data_y_base + 80)
    weather_icon = icons.get_scaled_image(get_forecats_weather_icon(data['WeatherSymbol3'], is_daylight, images, fonts, config), icon_width)
    image.paste(weather_icon, icon_position, weather_icon)

    # Warning icon
    if (utils.show_temperatur_warning_icon(data["Temperature"], date_local, config)):
      warning_icon = icons.get_scaled_image(images['misc']['warning'], 50)
      image.paste(warning_icon, (icon_position[0] + weather_icon.width - 2*warning_icon.width//3, icon_position[1] + weather_icon.height - 2*warning_icon.height//3), warning_icon)

    # Temperature
    utils.draw_quantity(draw, (x_base + i*x_step, data_y_base + 350), str(round(data["Temperature"])), '°C', fonts)
    # Wind speed
    utils.draw_quantity(draw, (x_base + i*x_step, data_y_base + 420), str(round(data["WindSpeedMS"])), 'm/s', fonts)

    # Cloud cover
    cloud_cover_raw = data["TotalCloudCover"]
    cloud_cover = math.nan if math.isnan(cloud_cover_raw) else cloud_cover_raw / 100 * 8
    cloud_cover_icon = icons.get_scaled_image(utils.get_cloud_cover_icon(cloud_cover, images, fonts, config), 160)
    image.paste(cloud_cover_icon, (x_base + i*x_step - cloud_cover_icon.width//2, data_y_base + 440), cloud_cover_icon)

    # Wind direction
    wind_image = icons.get_scaled_image(images['misc']['wind_icon'], 160)
    wind_image_rot = wind_image.rotate(-data['WindDirection'] + 180, fillcolor=0xff, resample=Image.BICUBIC)
    image.paste(wind_image_rot, (x_base + i*x_step - wind_image_rot.width//2, data_y_base + 440), wind_image_rot)

  # Borders
  if (config.getboolean('DRAW_PANEL_BORDERS')):
    draw.polygon([(0, 0), (x_size-1, 0), (x_size-1, y_size-1), (0, y_size-1), (0, 0)])

  return (image, position)


def get_forecats_weather_icon(weather_symbol_3, is_daylight: bool, images: Icons, fonts: Fonts, config: SectionProxy) -> Image.Image:
  if (config.getboolean('RANDOMIZE_WEATHER_ICONS')):
    icon_set = images['forecast'][random.choice(list(images['forecast'].keys()))]
    return utils.get_icon_variant(is_daylight, icon_set)

  if (math.isnan(weather_symbol_3)):
    return utils.get_missing_weather_icon_icon(math.nan, is_daylight, images, fonts)

  icon_index = round(weather_symbol_3)
  if (icon_index not in images['forecast']):
    return utils.get_missing_weather_icon_icon(icon_index, is_daylight, images, fonts)

  icon_set = images['forecast'][icon_index]
  return utils.get_icon_variant(is_daylight, icon_set)
