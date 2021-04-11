observation_mapping = {
  0:  {'day': 'no_phenomenon'},
  10: {'day': 'mist'},
  20: {'day': 'fog'},
  # 21: {'day': 'rain_mild'}, # Unknown form
  22: {'day': 'drizzle'},
  23: {'day': 'rain'},
  24: {'day': 'snow'},
  25: {'day': 'rain_icing'}, 
  30: {'day': 'fog'},
  31: {'day': 'fog'},
  32: {'day': 'fog'},
  33: {'day': 'fog'},
  34: {'day': 'fog'},
  # 40: {'day': 'rain'}, # Unknown form
  # 41: {'day': 'rain_mild'}, # Unknown form
  # 42: {'day': 'rain_strong'}, # Unknown form
  50: {'day': 'drizzle_mild'},
  51: {'day': 'drizzle_mild'},
  52: {'day': 'drizzle'},
  53: {'day': 'drizzle_strong'},
  54: {'day': 'drizzle_mild_icing'},
  55: {'day': 'drizzle_icing'},
  56: {'day': 'drizzle_strong_icing'},
  60: {'day': 'rain_mild'},
  61: {'day': 'rain_mild'},
  62: {'day': 'rain'},
  63: {'day': 'rain_strong'},
  64: {'day': 'rain_mild_icing'},
  65: {'day': 'rain_icing'},
  66: {'day': 'rain_strong_icing'},
  67: {'day': 'sleet_mild_2'},
  68: {'day': 'sleet_2'},
  70: {'day': 'snow'},
  71: {'day': 'snow_mild'},
  72: {'day': 'snow'},
  73: {'day': 'snow_strong'},
  80: {'day': 'partially_cloudy_rain_mild', 'night': 'partially_cloudy_rain_mild_night'},
  81: {'day': 'partially_cloudy_rain_mild', 'night': 'partially_cloudy_rain_mild_night'},
  82: {'day': 'partially_cloudy_rain', 'night': 'partially_cloudy_rain_night'},
  83: {'day': 'partially_cloudy_rain_strong', 'night': 'partially_cloudy_rain_strong_night'},
  84: {'day': 'partially_cloudy_rain_horrible', 'night': 'partially_cloudy_rain_horrible_night'},
  85: {'day': 'partially_cloudy_snow_mild', 'night': 'partially_cloudy_snow_mild_night'},
  86: {'day': 'partially_cloudy_snow', 'night': 'partially_cloudy_snow_night'},
  87: {'day': 'partially_cloudy_snow_strong', 'night': 'partially_cloudy_snow_strong_night'},
  89: {'day': 'partially_cloudy_hail_rain', 'night': 'partially_cloudy_hail_rain_night'}
}

forecast_mapping = {
  1:  {'day': 'clear', 'night': 'clear_night'},
  2:  {'day': 'partially_cloudy', 'night': 'partially_cloudy_night'},
  3:  {'day': 'clouds'},
  21: {'day': 'partially_cloudy_rain_mild', 'night': 'partially_cloudy_rain_mild_night'},
  22: {'day': 'partially_cloudy_rain', 'night': 'partially_cloudy_rain_night'},
  23: {'day': 'partially_cloudy_rain_strong', 'night': 'partially_cloudy_rain_strong_night'},
  31: {'day': 'rain_mild'},
  32: {'day': 'rain'},
  33: {'day': 'rain_strong'},
  41: {'day': 'partially_cloudy_snow_mild', 'night': 'partially_cloudy_snow_mild_night'},
  42: {'day': 'partially_cloudy_snow', 'night': 'partially_cloudy_snow_night'},
  43: {'day': 'partially_cloudy_snow_strong', 'night': 'partially_cloudy_snow_strong_night'},
  51: {'day': 'snow_mild'},
  52: {'day': 'snow'},
  53: {'day': 'snow_strong'},
  61: {'day': 'partially_cloudy_thunder', 'night': 'partially_cloudy_thunder_night'},
  62: {'day': 'partially_cloudy_thunder_strong', 'night': 'partially_cloudy_thunder_strong_night'},
  63: {'day': 'thunder'},
  64: {'day': 'thunder_strong'},
  71: {'day': 'partially_cloudy_sleet_mild', 'night': 'partially_cloudy_sleet_mild_night'},
  72: {'day': 'partially_cloudy_sleet', 'night': 'partially_cloudy_sleet_night'},
  73: {'day': 'partially_cloudy_sleet_strong', 'night': 'partially_cloudy_sleet_strong_night'},
  81: {'day': 'sleet_mild_2'},
  82: {'day': 'sleet_2'},
  83: {'day': 'sleet_strong_2'},
  91: {'day': 'mist'},
  92: {'day': 'fog'},
}

misc_icons = [
  ('wind_icon', 160), 
  ('sunrise', 200), 
  ('sunset', 200), 
  ('no_wifi', 200),
  ('battery_full', 120),
  ('battery_75', 120),
  ('battery_50', 120),
  ('battery_25', 120),
  ('battery_empty', 120),
  ('cloud_cover_0', 160),
  ('cloud_cover_1', 160),
  ('cloud_cover_2', 160),
  ('cloud_cover_3', 160),
  ('cloud_cover_4', 160),
  ('cloud_cover_5', 160),
  ('cloud_cover_6', 160),
  ('cloud_cover_7', 160),
  ('cloud_cover_8', 160),
  ('cloud_cover_9', 160),
]

# FMI symbol descriptions: https://www.ilmatieteenlaitos.fi/latauspalvelun-pikaohje
