from PIL import Image
import utils
import icons
from configparser import SectionProxy
from type_alias import Datetime, WeatherWarning, Icons


def draw_warning_icons(temperature: float, date_local: Datetime, images: Icons, image: Image.Image, weather_icon: Image.Image, icon_position: tuple[int, int], config: SectionProxy):
  weather_warning_level = utils.get_weather_warning_level(temperature, date_local, config)
  if (weather_warning_level == WeatherWarning.WARNING):
    warning_icon = icons.get_scaled_image(images['misc']['warning'], 50)
    image.paste(warning_icon, (icon_position[0] + weather_icon.width - 2*warning_icon.width//3, icon_position[1] + weather_icon.height - 2*warning_icon.height//3), warning_icon)

  if (weather_warning_level == WeatherWarning.CRITICAL):
    warning_icon_margin = 10
    warning_icon = icons.get_scaled_image(images['misc']['warning'], 50)
    image.paste(warning_icon, (icon_position[0] + weather_icon.width - 2*warning_icon.width//3, icon_position[1] + weather_icon.height - 2*warning_icon.height//3), warning_icon)
    image.paste(warning_icon, (icon_position[0] + weather_icon.width - 2*warning_icon.width//3 - warning_icon.width - warning_icon_margin, icon_position[1] + weather_icon.height - 2*warning_icon.height//3), warning_icon)
