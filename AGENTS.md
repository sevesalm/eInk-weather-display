# AGENTS.md

Guidance for coding agents working in this repository. Human-oriented docs: [README.md](README.md), [DEVELOPMENT.md](DEVELOPMENT.md), [full_install.md](full_install.md).

## Project

A Python app that renders a weather dashboard (FMI Open API observations/forecasts, RuuviTag and Home Assistant sensors, sun/moon data) into a grayscale image and draws it on a Waveshare 7.8"/10.3" e-Ink display (IT8951 controller) on a Raspberry Pi. Development happens on macOS; the app is deployed to the Pi over SSH.

## Layout

- `eInk-weather-display/` – the app. Flat module layout, no package; modules import each other by bare name (`import utils`).
  - `weather-display.py` – entry point. Loads config, fonts, icons, does an initial refresh, then runs an APScheduler cron job every minute (full refresh every `refresh_full_interval`, partial every `refresh_partial_interval`). In dev mode it refreshes once and exits.
  - `refresh.py` – fetches data, draws panels, pastes them into the full image, then saves a PNG (dev mode) or calls the C library in a forked subprocess with a timeout.
  - `*_panel.py` – each returns a PIL image for one region (observation, sensor, forecast, celestial, info).
  - `weather_data.py` (FMI API), `weather_data_mock.py` (random data), `sensor_data.py` (Ruuvi/Home Assistant), `celestial.py` (PyEphem), `feels_like_temperature.py`.
  - `app_config.py` – pydantic `AppConfig` loaded from `config.toml` (`extra='forbid'`). `config_example.toml` documents every option.
  - `type_alias.py` – shared `TypedDict`s and type aliases.
  - `lib/epd78.so`, `lib/epd37.so` – prebuilt ARM shared libraries loaded with `ctypes`. Only `epd78.so` is used now.
  - `test/` – `unittest` tests.
- `clib78/` (7.8"/10.3" IT8951) and `clib/` (legacy 3.7") – C sources for the display libraries. Built on the Pi against `bcm2835` via `scripts/compile.sh`.
- `svg_icons/` – source icons. PNGs in `eInk-weather-display/png_icons/` are generated and gitignored.
- `scripts/` – `deploy.sh`, `compile.sh`, `convert.sh`, `install_deps.sh`, etc. Remote scripts read `scripts/config.env` (copy from `config.env.example`; gitignored).
- `requirements/` – `common.txt` (app), `development.txt` (+ ruff), `raspberry.txt` (+ Pi-only: `RPi.GPIO`, `spidev`, `bleson`, `ruuvitag-sensor`).

## Commands

Run from the repo root with the `.venv` activated (Python 3.14, managed with `uv`):

```sh
uv pip install -r requirements/development.txt
python -m compileall -q .                          # CI: code compiles
ruff check                                         # CI: lint
python -m unittest discover -s eInk-weather-display  # CI: tests
```

Run all three before finishing a change; CI ([.github/workflows/default.yml](.github/workflows/default.yml)) runs exactly these.

To render the display locally, see [DEVELOPMENT.md](DEVELOPMENT.md#running-the-app-locally): generate PNG icons with `./scripts/convert.sh`, create `eInk-weather-display/config.toml` with `dev_mode = true` and the random-data flags, then run `python weather-display.py` **from inside `eInk-weather-display/`** (config, fonts, icons and `lib/` are resolved relative to the CWD). Output is `image.png`; check it visually after any drawing change.

## Code style

- **2-space indentation**, line length 250 (see [ruff.toml](ruff.toml)). Don't reformat to 4 spaces or run a formatter over untouched code; quote style is preserved as-is.
- Full type hints on functions; reuse aliases from `type_alias.py` (`Fonts`, `Icons`, `Datetime`, …).
- Get loggers with `logging.getLogger(__name__)` or accept a `logger` parameter, following the surrounding code. Use `logger.exception` for unexpected errors.
- Keep Pi-only imports (`ruuvitag_sensor`, `RPi.GPIO`, etc.) conditional/lazy so the app, tests and CI run on macOS/Linux without them.
- Tests use `unittest` and import app modules by bare name (`from utils import roundToString`); add new tests under `eInk-weather-display/test/`.

## Gotchas

- Adding a config option means updating `AppConfig` in `app_config.py` **and** `config_example.toml`; unknown keys are rejected at startup.
- The display is 1872×1404, 8-bit grayscale (`'L'` mode) downsampled by the C library to `bits_per_pixel`. Prefer high-contrast drawing; subtle grays may disappear.
- FMI data and icon mapping (`icon_mapping.py`, [weather_icon_codes.md](weather_icon_codes.md)) are Finland-specific.
- `HomeAssistant` sensors fetch real data even in dev mode; random sensor data is only generated for `Ruuvi` sensors.
- Don't commit `config.toml`, `scripts/config.env`, `png_icons/`, `image.png` or `logger.log`.
- The `.so` files can't be rebuilt locally; C changes must be compiled on the Pi with `scripts/compile.sh`, which copies the results back into `eInk-weather-display/lib/`.
- `deploy.sh` and `compile.sh` act on a real device over SSH; don't run them unless asked.
