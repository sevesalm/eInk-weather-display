# Configuration

The app is configured with two files:

- [`eInk-weather-display/config.toml`](#app-configuration-configtoml) configures the app itself. It is deployed to the Raspberry Pi along with the app.
- [`scripts/config.env`](#deployment-configuration-scriptsconfigenv) tells the helper scripts (`deploy.sh`, `compile.sh`) where to deploy. It stays on the development machine.

Both files are ignored by git.

## App configuration (`config.toml`)

Create `eInk-weather-display/config.toml` from [config_example.toml](eInk-weather-display/config_example.toml):

```sh
cp eInk-weather-display/config_example.toml eInk-weather-display/config.toml
```

The file is [TOML](https://toml.io). It is validated on startup against [`AppConfig`](eInk-weather-display/app_config.py): missing required options, unknown options, wrong types and out-of-range values stop the app with an error that names the option. The previous `config.ini` format is no longer supported.

All top-level options are required unless marked optional. `[home_assistant]` and `[[sensors]]` are tables and go after all top-level options, since in TOML every key after a table header belongs to that table.

### Development

| Option | Type | Description |
| --- | --- | --- |
| `dev_mode` | bool | `true`: render once, save the image to a PNG file and exit. `false`: draw on the e-Ink display and keep updating it. Set to `false` on the Raspberry Pi. |
| `dev_mode_output_filename` | string | File name of the PNG saved in dev mode, relative to the `eInk-weather-display` directory, e.g. `"image.png"`. |
| `dev_mode_random_weather_data` | bool | Use random weather data instead of the FMI API. Only applies when `dev_mode = true`. |
| `dev_mode_random_sensor_data` | bool | Use random readings for `Ruuvi` sensors instead of listening to Bluetooth. Only applies when `dev_mode = true`. `HomeAssistant` sensors always fetch real data. |

In dev mode the info panel also shows `(DEV MODE)`. See [DEVELOPMENT.md](DEVELOPMENT.md#running-the-app-locally) for running the app locally.

### Location

| Option | Type | Description |
| --- | --- | --- |
| `fmi_location` | string | Place name used for the FMI forecast, e.g. a city or neighborhood (`"Helsinki"`). FMI resolves it to coordinates, which are also used for the sunrise, sunset and Moon data. Only locations covered by FMI (Finland and nearby) work. |
| `fmi_observation_location_override` | string, optional | Place name used for the observations instead of `fmi_location`. Useful when the nearest observation station is listed under a different place name. |
| `override_name` | string | Location name shown when the FMI forecast can't be fetched. |
| `override_latitude` | float, -90…90 | Latitude used for the celestial data when the FMI forecast can't be fetched. |
| `override_longitude` | float, -180…180 | Longitude used for the celestial data when the FMI forecast can't be fetched. |

### Display

| Option | Type | Description |
| --- | --- | --- |
| `epd_model` | `"7.8"` or `"10.3"` | Display model. Both are 1872×1404 and use the same IT8951 library. |
| `epd_voltage` | int, > 0 | The display's VCOM voltage in millivolts, without the minus sign. It is printed on the display's FPC cable (e.g. `-1.37V` → `1370`). A wrong value gives a washed-out or too dark image. |
| `bits_per_pixel` | `1`, `2` or `4` | Gray levels sent to the display (2, 4 or 16). Fewer bits are faster to transfer but lose shades. |
| `rotate_180` | bool | Rotate the image by 180 degrees, e.g. when the display is mounted upside down. |
| `mirror_horizontal` | bool | Mirror the image horizontally. Needed for the 10.3" model, whose controller draws the image mirrored. |
| `draw_borders` | bool | Draw thin dividers between the panels. |
| `draw_panel_borders` | bool | Debugging aid: draw a border around each panel. |

### Refresh schedule

| Option | Type | Description |
| --- | --- | --- |
| `update_interval` | int, seconds, 1…3600, divides 3600 | How often the data is fetched and the image is redrawn. Only the areas that changed are updated on the display, which is fast and doesn't flash. |
| `full_refresh_interval` | int, seconds, 1…3600, divides 3600 | How often the whole display is cleared and redrawn to remove ghosting left by partial updates. A full refresh flashes the display. |

Both intervals must divide an hour evenly (e.g. 60, 300, 600, 900, 1800, 3600) since runs are scheduled in slots counted from the start of each hour: updates run at multiples of `update_interval` past the hour, and full refreshes on the first update at or after 5 minutes past the hour plus multiples of `full_refresh_interval`. A full refresh that is missed (e.g. the update failed) is done on the next update.

### Temperature warnings

A warning or extreme warning icon is shown next to an observed or forecast temperature that reaches one of these thresholds. All values are in °C.

| Option | Type | Description |
| --- | --- | --- |
| `high_temperature_warning_threshold` | int | Warning when the temperature is >= this. |
| `extreme_high_temperature_warning_threshold` | int, >= `high_…` | Extreme warning when the temperature is >= this. |
| `low_temperature_warning_threshold` | int, <= `high_…` | Warning when the temperature is <= this. |
| `extreme_low_temperature_warning_threshold` | int, <= `low_…` | Extreme warning when the temperature is <= this. |
| `tropical_night_temperature_warning_threshold` | int, > `low_…` and <= `high_…` | Warning when the temperature is >= this between 22:00 and 07:59 (a "tropical night"). |

### Sensors

| Option | Type | Description |
| --- | --- | --- |
| `sensor_poll_timeout` | int, seconds, > 0 | How long RuuviTag broadcasts are listened to on each update. Increase it if readings are missing due to weak Bluetooth reception. |

Sensors are listed as `[[sensors]]` tables, one per sensor, in the order they are shown. The sensor panel has room for at most 6. Sensor names must be unique. With no sensors, the panel is left empty.

**RuuviTag** sensors are read over Bluetooth:

```toml
[[sensors]]
type = "Ruuvi"
name = "Balcony"           # Shown on the display
mac = "AA:BB:CC:DD:EE:FF"  # The RuuviTag's MAC address, any case
```

**Home Assistant** sensors read the current state of Home Assistant entities and need the [`[home_assistant]`](#home-assistant-optional) table; without it the app doesn't start:

```toml
[[sensors]]
type = "HomeAssistant"
name = "Living room"
temperature_sensor_id = "sensor.living_room_temperature"  # Entity id of the temperature (°C)
humidity_sensor_id = "sensor.living_room_humidity"        # Entity id of the relative humidity (%)
battery_sensor_id = "sensor.living_room_battery"          # Optional: entity id of the battery level (%)
```

### Home Assistant (optional)

Needed only for `HomeAssistant` sensors.

```toml
[home_assistant]
url = "http://homeassistant.local:8123"
bearer_token = "YOUR_LONG_LIVED_ACCESS_TOKEN"
```

| Option | Type | Description |
| --- | --- | --- |
| `url` | URL | Base URL of the Home Assistant instance. |
| `bearer_token` | string | A long-lived access token, created in Home Assistant under your user profile → Security. The token is sent with every request, so prefer an `https://` URL where available. |

## Deployment configuration (`scripts/config.env`)

The scripts in [scripts/](scripts) that act on the Raspberry Pi over SSH read `scripts/config.env`. Create it from [config.env.example](scripts/config.env.example):

```sh
cp scripts/config.env.example scripts/config.env
```

It is a Bash file sourced by the scripts, so use `NAME=value` without spaces around `=`.

| Variable | Description |
| --- | --- |
| `HOSTNAME` | SSH destination of the Raspberry Pi: an IP address, a hostname or a `Host` alias from `~/.ssh/config`. Can include the user, e.g. `pi@weather.local`. |
| `APP_ROOT_DIRECTORY` | Directory on the Raspberry Pi under which the app is installed. Can be relative to the SSH user's home directory. |
| `VENV_ROOT_DIRECTORY` | Directory on the Raspberry Pi under which the Python virtual env is created. Can be relative to the SSH user's home directory. |
| `APP_NAME` | Name of the app directory. Defaults to `eInk-weather-display`; usually no need to change. |
| `VENV_NAME` | Name of the virtual env directory. Defaults to `APP_NAME`. |

The app is installed to `APP_ROOT_DIRECTORY/APP_NAME` and the virtual env to `VENV_ROOT_DIRECTORY/VENV_NAME`. See [full_install.md](full_install.md#install-eink-weather-display) for deploying.
