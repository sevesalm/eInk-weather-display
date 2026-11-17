import unittest
from datetime import datetime
from zoneinfo import ZoneInfo
from utils import roundToString, utc_datetime_string_to_local_datetime


class TestUtils(unittest.TestCase):
  def test_nan(self):
    result = roundToString(float('nan'))
    self.assertEqual(result, '?')

  def test_float_no_decimals(self):
    result = roundToString(1.15)
    self.assertEqual(result, '1')

  def test_float_one_decimals(self):
    result = roundToString(1.16, 1)
    self.assertEqual(result, '1.2')

  def test_naive_datetime_string_is_utc(self):
    result = utc_datetime_string_to_local_datetime('2026-01-01T12:00:00')
    self.assertEqual(result, datetime(2026, 1, 1, 12, tzinfo=ZoneInfo('UTC')))

  def test_aware_datetime_string_keeps_timezone(self):
    result = utc_datetime_string_to_local_datetime('2026-01-01T12:00:00+02:00')
    self.assertEqual(result, datetime(2026, 1, 1, 10, tzinfo=ZoneInfo('UTC')))


if __name__ == '__main__':
    unittest.main()
