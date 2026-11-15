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

`requirements/development.txt` includes the common app dependencies and `ruff`. The Raspberry Pi only dependencies (`RPi.GPIO`, `spidev`, `bleson`, `ruuvitag-sensor`) are not needed on macOS.

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

CI ([.github/workflows/default.yml](.github/workflows/default.yml)) also checks that all the code compiles:

```sh
python -m compileall -q .
```

## Running the app locally

In dev mode the app draws the display image once, saves it as a PNG file and exits. The e-Ink display library is not loaded, and the weather and sensor data can be replaced with random data.

### 1. Generate the PNG icons

The icons are drawn from the SVG files in [svg_icons](svg_icons) and are not committed to the repository. Convert them once, and again whenever the SVGs change:

```sh
brew install librsvg
mkdir -p eInk-weather-display/png_icons
./scripts/convert.sh
```

### 2. Create a config file

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

### 3. Run

The app reads `config.toml`, fonts and icons relative to the current directory, so run it from the `eInk-weather-display` directory:

```sh
cd eInk-weather-display
python weather-display.py
open image.png
```

Logs are printed to the terminal and written to `logger.log`.
