import random
from dateutil.parser import parse
import pytz
from PIL import Image, ImageDraw, ImageOps
from celestial import get_is_day
import logging
from weather import get_forecasts
import utils

def get_forecasts_panel(forecast_images, misc_images, fonts, config):
  logger = logging.getLogger(__name__)
  logger.info('Generating forecast panel')
  (forecasts, first_position) = get_forecasts(config.get('FMI_LOCATION'), 6, 6)
  logger.info('Received data: %s', repr(forecasts))
  x_size = 480
  y_size = 180
  dates = sorted(forecasts.keys())
  image = Image.new('L', (x_size, y_size), 0xff) 
  draw = ImageDraw.Draw(image)
  for date, i in zip(dates, range(len(dates))):
    isDay = get_is_day(first_position, date)
    data = forecasts[date]
    weather_symbol = round(data['WeatherSymbol3'])
    utc_dt = parse(date).replace(tzinfo=pytz.utc)
    date_formatted = utc_dt.astimezone(tz=None).strftime('%-H:%M')
    # Time
    draw.text((50 + i*75, 10), date_formatted, font = (fonts['font_sm'] if date_formatted != "15:00" else fonts['font_sm_bold']), fill = 0, anchor = 'mt')
    # Icon
    randomize_weather_icons = config.getboolean('RANDOMIZE_WEATHER_ICONS')
    if(weather_symbol in forecast_images or randomize_weather_icons):
      if(not randomize_weather_icons):
        image_set = forecast_images.get(weather_symbol) 
      else: 
        image_set = forecast_images[random.choice(list(forecast_images.keys()))]
      if(not isDay and 'night' in image_set):
        weather_icon = image_set['night']
      else:
        weather_icon = image_set['day']
      image.paste(weather_icon, (int(i*75 + 50 - weather_icon.width/2), 30))
    else:
      draw.text((50 + i*75, 70), f'(NA: {weather_symbol})', font = fonts['font_sm'], fill = 0, anchor = 'mm')

    # Numeric info
    utils.draw_quantity(draw, (50 + i*75, 120), str(round(data["Temperature"])), '°C', fonts)
    utils.draw_quantity(draw, (50 + i*75, 140), str(round(data["WindSpeedMS"])), 'm/s', fonts)
  
    wind_image = misc_images['wind_arrow'] 
    wind_image_rot = wind_image.rotate(-data['WindDirection'] + 180, fillcolor = 0xff)
    image.paste(wind_image_rot, (int(i*75 + 50 - wind_image.width/2), 150))

  # Borders
  if (config.getboolean('DRAW_PANEL_BORDERS')):
    draw.polygon([(0, 0), (x_size-1, 0), (x_size-1, y_size-1), (0, y_size-1), (0, 0)])
    
  return (image, first_position)