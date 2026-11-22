# Development

How to run the tests, lint the code and run the app locally on macOS without the e-Ink display or real sensors.

All commands are run from the repository root unless stated otherwise.

## Setup

Install [uv](https://docs.astral.sh/uv/) and create a virtual environment. CI uses Python 3.14, so use the same version locally:

```sh
brew install uv
uv venv --python 3.14
. .venv/bin/activate
uv pip install -r requirements/development.txt
```

`requirements/development.txt` includes the common app dependencies, `ruff` and `ty`. The Raspberry Pi only dependencies (`RPi.GPIO`, `spidev`, `bleson`, `ruuvitag-sensor`) are not needed on macOS.

Note: Avoid Python versions newer than the pinned packages support. For example, `Pillow==11.3.0` has no prebuilt wheel for Python 3.15 and fails to install.

## Running tests

```sh
python -m unittest discover -s eInk-weather-display
```

## Linting

The linter is [ruff](https://docs.astral.sh/ruff/), configured in [ruff.toml](ruff.toml):

```sh
ruff check
```

Many issues can be fixed automatically with `ruff check --fix`.

The type checker is [ty](https://docs.astral.sh/ty/), configured in [ty.toml](ty.toml). It finds the activated `.venv` automatically:

```sh
ty check
```

CI ([.github/workflows/default.yml](.github/workflows/default.yml)) also checks that all the code compiles:

```sh
python -m compileall -q .
```

## Running the app locally

In dev mode the app draws the display image once, saves it as a PNG file and exits. The e-Ink display library is not loaded, and the weather and sensor data can be replaced with random data.

The icons are rendered at startup straight from the SVG files in [eInk-weather-display/svg_icons](eInk-weather-display/svg_icons) with [resvg-py](https://pypi.org/project/resvg-py/), so there is no conversion step. Edit an SVG and run the app again to see the change. The [icon gallery](eInk-weather-display/svg_icons/README.md) shows the SVGs directly, so it stays up to date too.

### 1. Create a config file

```sh
cp eInk-weather-display/config_example.toml eInk-weather-display/config.toml
```

`config.toml` is ignored by git. Set these values in it:

```toml
dev_mode = true                      # Save to a PNG instead of drawing on the display
dev_mode_output_filename = "image.png"
dev_mode_random_weather_data = true  # Use fake data instead of the FMI API
dev_mode_random_sensor_data = true   # Use fake data instead of reading RuuviTags over Bluetooth
```

Random sensor data is only generated for `Ruuvi` type sensors, so add one or more with any MAC address to fill the sensor panel:

```toml
[[sensors]]
type = "Ruuvi"
name = "Living room"
mac = "AA:BB:CC:DD:EE:01"

[[sensors]]
type = "Ruuvi"
name = "Balcony"
mac = "AA:BB:CC:DD:EE:02"
```

`HomeAssistant` type sensors always fetch real data from the configured Home Assistant instance, even in dev mode.

Set `dev_mode_random_weather_data = false` to render real FMI data for `fmi_location`.

### 2. Run

The app reads `config.toml`, fonts and icons from the `eInk-weather-display` directory and writes the image and the log there, so it can be run from any directory:

```sh
python eInk-weather-display/weather-display.py
open eInk-weather-display/image.png
```

Logs are printed to the terminal and written to `eInk-weather-display/logger.log`.
