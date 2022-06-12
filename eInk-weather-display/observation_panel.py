import math
from PIL import Image, ImageDraw
import logging
from celestial import get_is_daylight
import utils
import icons
from feels_like_temperature import get_feels_like_temperature
from configparser import SectionProxy
from type_alias import Icons, Fonts, WeatherData, ApiData


def get_observation_icon(wawa: float, cloud_coverage: float, is_daylight: bool, images: Icons, fonts: Fonts, config: SectionProxy) -> Image.Image:
  if (wawa not in images['observation']):
    return utils.get_missing_weather_icon_icon(wawa, is_daylight, images, fonts)

  # For codes 0 to 3 and 20 to 26, let's use cloud cover to determine the icon set
  if(((0 <= wawa <= 3) or (20 <= wawa <= 26)) and not math.isnan(cloud_coverage)):
    if(cloud_coverage <= 1):  # Clear sky
      icon_set = images['forecast'].get(1)
    elif(2 <= cloud_coverage <= 6):  # Partially cloudy
      icon_set = images['forecast'].get(2)
    elif(7 <= cloud_coverage <= 8):  # Overcast
      icon_set = images['forecast'].get(3)
    else:  # Lolwut?
      icon_set = images['observation'].get(0)
  else:
    icon_set = images['observation'].get(int(wawa))
  if (icon_set is None):
    raise Exception('icon_set not found')
  return utils.get_icon_variant(is_daylight, icon_set)


def get_observation_panel(observation_data: WeatherData, radiation_data: ApiData, images: Icons, fonts: Fonts, config: SectionProxy) -> Image.Image:
  logger = logging.getLogger(__name__)
  logger.info('Generating observation panel')
  icon_size = 280
  (observations, position, position_name, _) = observation_data
  latest_date = max(observations.keys())
  latest_date_local = utils.utc_datetime_string_to_local_datetime(latest_date)
  is_daylight = get_is_daylight(position, latest_date)
  x_size = 700
  y_size = 550
  latest = observations[latest_date]
  image = Image.new('L', (x_size, y_size), 0xff)
  draw = ImageDraw.Draw(image)

  utils.draw_title(draw, fonts['font_sm'], 'OUT', position_name, fonts['font_xxs'])

  delimiter_x = 290
  data_y_base = 100

  # Feels like
  if(radiation_data):
    latest_radiation_date = max(radiation_data.keys())
    latest_dir_1min = radiation_data[latest_radiation_date]["dir_1min"]
  else:
    latest_dir_1min = 0.0

  temp_feels = get_feels_like_temperature(latest["t2m"], latest["ws_10min"], latest_dir_1min, latest["rh"]/100.0)

  # Temperature
  utils.draw_quantity(draw, (delimiter_x, data_y_base + 120), str(round(latest["t2m"], 1)), '°C', fonts, 'font_lg', 'font_sm')

  # Feels like temperature
  utils.draw_quantity(draw, (delimiter_x, data_y_base + 210), str(round(temp_feels)), '°C', fonts)
  temperature_feel_icon = icons.get_scaled_image_by_height(images['misc']['temperature_feel'], 70)
  image.paste(temperature_feel_icon, (10, data_y_base + 210-65), temperature_feel_icon)

  # Relative humidity
  utils.draw_quantity(draw, (delimiter_x, data_y_base + 290), str(round(latest["rh"])), '%', fonts)
  humidity_icon = icons.get_scaled_image(images['misc']['humidity'], 70)
  image.paste(humidity_icon, (10, data_y_base + 290-65), humidity_icon)

  # Barometric pressure
  utils.draw_quantity(draw, (delimiter_x, data_y_base + 370), str(round(latest["p_sea"])), 'hPa', fonts)
  pressure_icon = icons.get_scaled_image(images['misc']['pressure'], 70)
  image.paste(pressure_icon, (10, data_y_base + 370-65), pressure_icon)

  # Wind speed
  utils.draw_quantity(draw, (delimiter_x, data_y_base + 450), f'{round(latest["ws_10min"])} – {round(latest["wg_10min"])}', 'm/s', fonts)
  wind_icon = icons.get_scaled_image(images['misc']['wind'], 70)
  image.paste(wind_icon, (10, data_y_base + 450-65), wind_icon)

  # Cloud cover
  cloud_coverage = latest['n_man']
  margin = 15
  right_column_x_base = x_size//2 + margin + 30
  cloud_cover_icon = icons.get_scaled_image(utils.get_cloud_cover_icon(cloud_coverage, images, fonts, config), 160)
  image.paste(cloud_cover_icon, (right_column_x_base + icon_size//2 - cloud_cover_icon.width//2, data_y_base), cloud_cover_icon)

  # Wind direction
  w_dir = latest['wd_10min']
  if(not math.isnan(w_dir)):
    wind_image = icons.get_scaled_image(images['misc']['wind_icon'], 160)
    wind_image_rot = wind_image.rotate(-w_dir + 180, fillcolor=0xff, resample=Image.BICUBIC)
    image.paste(wind_image_rot, (right_column_x_base + icon_size//2 - cloud_cover_icon.width//2, data_y_base), wind_image_rot)

  # Weather icon
  y_top = y_size - icon_size - margin

  weather_icon = icons.get_scaled_image(get_observation_icon(latest['wawa'], cloud_coverage, is_daylight, images, fonts, config), icon_size)
  image.paste(weather_icon, (right_column_x_base, y_top), weather_icon)

  # Warning icon
  if (utils.show_temperatur_warning_icon(latest["t2m"], latest_date_local, config)):
    warning_icon = icons.get_scaled_image(images['misc']['warning'], 60)
    image.paste(warning_icon, (right_column_x_base + weather_icon.width - 2*warning_icon.width//3, y_top + weather_icon.height - 2*warning_icon.height//3), warning_icon)

  # Borders
  if (config.getboolean('DRAW_PANEL_BORDERS')):
    draw.polygon([(0, 0), (x_size-1, 0), (x_size-1, y_size-1), (0, y_size-1), (0, 0)])

  return image
