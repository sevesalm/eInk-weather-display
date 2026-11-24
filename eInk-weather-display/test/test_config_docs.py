import re
import tomllib
import unittest

from pydantic import BaseModel

from app_config import AppConfig, HomeAssistantConfig, HomeAssistantSensor, RuuviSensor, load_config
from paths import APP_DIR

CONFIG_EXAMPLE = APP_DIR / 'config_example.toml'
CONFIGURATION_MD = APP_DIR.parent / 'CONFIGURATION.md'

# Fields that are set by the app, not by the user
INTERNAL_FIELDS = {'id'}


def documented_fields(model: type[BaseModel]) -> set[str]:
  return set(model.model_fields) - INTERNAL_FIELDS


ALL_FIELDS = set().union(*(documented_fields(model) for model in (AppConfig, HomeAssistantConfig, RuuviSensor, HomeAssistantSensor)))


def uncomment_examples(text: str) -> str:
  '''Uncomments the commented-out TOML in the example (table headers and key = value lines), leaving the prose comments as is.'''
  return re.sub(r'^# ?(?=\[|[a-z0-9_]+ = )', '', text, flags=re.MULTILINE)


def option_names(text: str) -> set[str]:
  '''Keys (key = value) and table names ([table], [[table]]) in TOML, commented out or not, also in Markdown code blocks.'''
  keys = re.findall(r'^(?:# ?)?([a-z0-9_]+) = ', text, flags=re.MULTILINE)
  tables = re.findall(r'^(?:# ?)?\[\[?([a-z0-9_]+)\]', text, flags=re.MULTILINE)
  return set(keys) | set(tables)


class TestConfigDocs(unittest.TestCase):
  '''Keeps config_example.toml and CONFIGURATION.md in sync with AppConfig.'''

  def test_example_is_valid(self):
    load_config(CONFIG_EXAMPLE)

  def test_example_with_optional_sections_is_valid(self):
    config = AppConfig.model_validate(tomllib.loads(uncomment_examples(CONFIG_EXAMPLE.read_text())))
    self.assertIsNotNone(config.home_assistant)
    self.assertEqual({sensor.type for sensor in config.sensors}, {'Ruuvi', 'HomeAssistant'})

  def test_example_has_every_option(self):
    keys = option_names(CONFIG_EXAMPLE.read_text())
    self.assertEqual(ALL_FIELDS - keys, set(), 'Options missing from config_example.toml')
    self.assertEqual(keys - ALL_FIELDS, set(), 'Unknown options in config_example.toml')

  def test_configuration_md_has_every_option(self):
    text = CONFIGURATION_MD.read_text()
    # An option is documented in a table row (| `name` | ...) or in an example code block.
    # Lowercase only, so the uppercase config.env variables are left out.
    table_rows = set(re.findall(r'^\| `([a-z0-9_]+)` \|', text, flags=re.MULTILINE))
    documented = table_rows | option_names(text)
    self.assertEqual(ALL_FIELDS - documented, set(), 'Options missing from CONFIGURATION.md')
    self.assertEqual(documented - ALL_FIELDS, set(), 'Unknown options in CONFIGURATION.md')


if __name__ == '__main__':
  unittest.main()
