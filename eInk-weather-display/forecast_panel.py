import random
import math
from dateutil.parser import parse
import pytz
from PIL import Image, ImageDraw, ImageOps
from celestial import get_is_day
import logging
from weather import get_forecasts
import utils

def get_forecasts_panel(images, fonts, config):
  logger = logging.getLogger(__name__)
  logger.info('Generating forecast panel')
  count = 7
  x_size = 1872
  y_size = 800
  (forecasts, first_position, first_position_name) = get_forecasts(config.get('FMI_LOCATION'), count, 6)
  logger.info('Received data: %s', repr(forecasts))

  dates = sorted(forecasts.keys())
  image = Image.new('L', (x_size, y_size), 0xff) 
  draw = ImageDraw.Draw(image)

  utils.draw_title(draw, fonts['font_sm'], 'FORECAST', first_position_name, fonts['font_xxs'])

  data_y_base = 100

  for date, i in zip(dates, range(len(dates))):
    isDay = get_is_day(first_position, date)
    data = forecasts[date]
    utc_dt = parse(date).replace(tzinfo=pytz.utc)
    date_formatted = utc_dt.astimezone(tz=None).strftime('%-H:%M')
    x_step = x_size//count
    x_base = x_step//2

    # Time
    draw.text((x_base + i*x_step, data_y_base + 10), date_formatted, font = (fonts['font_sm'] if date_formatted != "15:00" else fonts['font_sm_bold']), fill = 0, anchor = 'mt')

    # Weather icon
    icon_position = (x_base + i*x_step - config.getint('ICON_WIDTH')//2, data_y_base + 80)
    weather_icon = get_forecats_weather_icon(data['WeatherSymbol3'], isDay, images, fonts, config)
    image.paste(weather_icon, icon_position)

    # Temperature
    utils.draw_quantity(draw, (x_base + i*x_step, data_y_base + 350), str(round(data["Temperature"])), '°C', fonts)
    # Wind speed
    utils.draw_quantity(draw, (x_base + i*x_step, data_y_base + 420), str(round(data["WindSpeedMS"])), 'm/s', fonts)
  
    # Cloud cover
    cloud_cover_raw = data["TotalCloudCover"]
    cloud_cover = math.nan if math.isnan(cloud_cover_raw) else cloud_cover_raw / 100 * 8
    cloud_cover_icon = utils.get_cloud_cover_icon(cloud_cover, images, fonts, config)
    image.paste(cloud_cover_icon, (x_base + i*x_step - cloud_cover_icon.width//2, data_y_base + 440), )

    # Wind direction
    wind_image = images['misc']['wind_icon'] 
    wind_image_rot = wind_image.rotate(-data['WindDirection'] + 180, fillcolor = 0xff, resample=Image.BICUBIC)
    image.paste(wind_image_rot, (x_base + i*x_step - wind_image_rot.width//2, data_y_base + 440), ImageOps.invert(wind_image_rot))

  # Borders
  if (config.getboolean('DRAW_PANEL_BORDERS')):
    draw.polygon([(0, 0), (x_size-1, 0), (x_size-1, y_size-1), (0, y_size-1), (0, 0)])
    
  return (image, first_position)

def get_forecats_weather_icon(weather_symbol_3, isDay, images, fonts, config):
  if (config.getboolean('RANDOMIZE_WEATHER_ICONS')):
    icon_set = images['forecast'][random.choice(list(images['forecast'].keys()))]
    return utils.get_icon_variant(isDay, icon_set)

  icon_index = math.nan if math.isnan(weather_symbol_3) else round(weather_symbol_3)
  if (not icon_index in images['forecast']):
    return utils.get_missing_weather_icon_icon(icon_index, images, fonts)

  icon_set = images['forecast'].get(icon_index) 
  return utils.get_icon_variant(isDay, icon_set)