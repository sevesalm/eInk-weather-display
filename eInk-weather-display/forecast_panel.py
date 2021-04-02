import random
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
  (forecasts, first_position) = get_forecasts(config.get('FMI_LOCATION'), count, 6)
  logger.info('Received data: %s', repr(forecasts))

  dates = sorted(forecasts.keys())
  image = Image.new('L', (x_size, y_size), 0xff) 
  draw = ImageDraw.Draw(image)

  utils.draw_title(draw, (260, 80), 'FORECAST', fonts)

  data_y_base = 100

  for date, i in zip(dates, range(len(dates))):
    isDay = get_is_day(first_position, date)
    data = forecasts[date]
    weather_symbol = round(data['WeatherSymbol3'])
    utc_dt = parse(date).replace(tzinfo=pytz.utc)
    date_formatted = utc_dt.astimezone(tz=None).strftime('%-H:%M')
    x_step = x_size//count
    x_base = x_step//2
    # Time
    draw.text((x_base + i*x_step, data_y_base + 10), date_formatted, font = (fonts['font_sm'] if date_formatted != "15:00" else fonts['font_sm_bold']), fill = 0, anchor = 'mt')
    # Icon
    randomize_weather_icons = config.getboolean('RANDOMIZE_WEATHER_ICONS')
    if(weather_symbol in images['forecast'] or randomize_weather_icons):
      if(not randomize_weather_icons):
        image_set = images['forecast'].get(weather_symbol) 
      else: 
        image_set = images['forecast'][random.choice(list(images['forecast'].keys()))]
      if(not isDay and 'night' in image_set):
        weather_icon = image_set['night']
      else:
        weather_icon = image_set['day']
      image.paste(weather_icon, (int(x_base + i*x_step - weather_icon.width/2), data_y_base + 80))
    else:
      draw.text((x_base + i*x_step, data_y_base + 200), f'(NA: {weather_symbol})', font = fonts['font_sm'], fill = 0, anchor = 'mm')

    # Numeric info
    utils.draw_quantity(draw, (x_base + i*x_step, data_y_base + 350), str(round(data["Temperature"])), '°C', fonts)
  
    # Wind icon
    wind_image = images['misc']['wind_icon'] 
    wind_image_rot = wind_image.rotate(-data['WindDirection'] + 180, fillcolor = 0xff, resample=Image.BICUBIC)
    image.paste(wind_image_rot, (x_base + i*x_step - wind_image_rot.width//2, data_y_base + 360))
    draw.text((x_base + i*x_step, data_y_base + 360 + wind_image_rot.height//2), str(round(data["WindSpeedMS"])), font=fonts['font_sm'], fill=0, anchor='mm')

  # Borders
  if (config.getboolean('DRAW_PANEL_BORDERS')):
    draw.polygon([(0, 0), (x_size-1, 0), (x_size-1, y_size-1), (0, y_size-1), (0, 0)])
    
  return (image, first_position)