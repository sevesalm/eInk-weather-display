def get_temp_chill(temp: float, wind: float) -> float:
  return 15 + (1 - 15/37)*temp + 15/37 * (wind + 1)**0.16 * (temp - 37)


def get_temp_heat(temp: float, humidity: float) -> float:
  if (temp < 14.5):
    return temp
  humidity_ref = 0.5
  return (1.8*temp - 0.55*(1-humidity)*(1.8*temp - 26) - 0.55*(1-humidity_ref)*26) / (1.8 * (1 - 0.55*(1 - humidity_ref)))


def get_d_temp_sun(radiation: float, wind: float) -> float:
  c_abs = 0.07
  return 0.7 * c_abs * max(radiation, 0) / (wind + 10) - 0.25


# Reference: https://tietopyynto.fi/tietopyynto/ilmatieteen-laitoksen-kayttama-tuntuu-kuin-laskentakaava/
def get_feels_like_temperature(temp: float, wind: float, radiation: float, humidity: float) -> float:
  temp_chill = get_temp_chill(temp, wind)
  temp_heat = get_temp_heat(temp, humidity)
  d_temp_sun = get_d_temp_sun(radiation, wind)
  temp_feels = temp + (temp_chill - temp) + (temp_heat - temp) + d_temp_sun
  return temp_feels
