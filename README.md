# Raspberry Pi e-Ink Weather Data Display

This application is a project for building a weather data display using [Raspberry Pi](https://www.raspberrypi.org/products/), [Waveshare e-Paper Display](https://www.waveshare.com/product/raspberry-pi/displays/e-paper.htm) and [RuuviTag sensors](https://ruuvi.com/ruuvitag-specs/). The goal of the project is to have an e-Ink display showing:

- Current weather observations (temperature, windspeed, humidity etc.)
- Near term weather forecast
- Weather data from RuuviTag sensors

The prototype hardware:

- [Raspberry Pi 3 Model B+](https://www.raspberrypi.org/products/raspberry-pi-3-model-b-plus/) computer
- [Waveshare 3.7" e-Paper HAT](https://www.waveshare.com/product/raspberry-pi/displays/e-paper/3.7inch-e-paper-hat.htm) e-Ink display
- [RuuviTag](https://ruuvi.com/ruuvitag-specs/) sensors

![prototype](images/weather-display.jpg)

## Development and Deployment

### Deployment

1. Clone this repository on Raspberry Pi
1. Create a venv and activate it
1. Install dependencies: `pip install -r requirements.txt`
1. Convert the SVG images: `./convert.sh` (install `rsvg-convert` if needed)
1. Start: `python weather-display.py`

### Development

The script [deploy.sh](scripts/deploy.sh.example) is a small helper which copies all the files over SSH to Raspberry Pi, activates venv and starts the application remotely using the [run.sh](scripts/run.sh.example) script. This is useful if you run your Raspberry Pi in headless mode.

Example scripts are provided. Please edit them to suit your needs.

## Observations and forecast data

The application shows real time weather observations and near term forecast data from the [open API by FMI](https://en.ilmatieteenlaitos.fi/open-data). The API offers accurate data updated regularly based on the given location.

## RuuviTag data

RuuviTag sensors measure temperature, barometric pressure and humidity every few seconds and broadcast it using Bluetooth 5. This data is read by Raspberry Pi and further showed on the display.

Note: Currently this feature is not implemented.

## Celestial data

The application shows sunrise and sunset times and the phase of the Moon. These are calculated using [PyEphem library](https://rhodesmill.org/pyephem/).

## Weather icons

The data from FMI API includes [WaWa and WeatherSymbol3](weather_icon_codes.md) codes which can be used to show a weather icon or a description to the user. There are a lot of free weather icons or icon fonts available in the Internet but it is hard to find one which covers all the codes FMI uses. For this reason I have created a set of weather icons for this need.

The weather icon set contains a unique icon for almost all weather codes. The icons were drawn programmatically in svg. Because the PILLOW library doesn't support SVG format, the icons have to be converted to PNG images using the provided [script](convert.sh) before usage.

The icons contain night variants for some icons. The night varian is used when the observation/forecast time is determined to happen after sunset but before sunrise - commonly know as "during the night".

## Used licenses

See the [fonts/README.md](fonts/README.md) for information about fonts used in this project and their licenses.
