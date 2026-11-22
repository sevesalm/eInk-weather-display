import unittest
from datetime import datetime
from zoneinfo import ZoneInfo
from utils import roundToString, utc_datetime_string_to_local_datetime, get_latest_full_refresh_slot, should_full_refresh


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

  def test_full_refresh_slot_same_hour(self):
    self.assertEqual(get_latest_full_refresh_slot(datetime(2026, 1, 1, 10, 30, 15), 3600), datetime(2026, 1, 1, 10, 5))
    self.assertEqual(get_latest_full_refresh_slot(datetime(2026, 1, 1, 10, 20), 900), datetime(2026, 1, 1, 10, 20))
    self.assertEqual(get_latest_full_refresh_slot(datetime(2026, 1, 1, 10, 34), 900), datetime(2026, 1, 1, 10, 20))

  def test_full_refresh_slot_previous_hour(self):
    self.assertEqual(get_latest_full_refresh_slot(datetime(2026, 1, 1, 10, 3), 3600), datetime(2026, 1, 1, 9, 5))
    self.assertEqual(get_latest_full_refresh_slot(datetime(2026, 1, 1, 0, 3), 900), datetime(2025, 12, 31, 23, 50))

  def test_full_refresh_at_slot(self):
    self.assertTrue(should_full_refresh(datetime(2026, 1, 1, 10, 5), datetime(2026, 1, 1, 9, 5), 3600))

  def test_no_full_refresh_between_slots(self):
    self.assertFalse(should_full_refresh(datetime(2026, 1, 1, 10, 6), datetime(2026, 1, 1, 10, 5), 3600))
    self.assertFalse(should_full_refresh(datetime(2026, 1, 1, 11, 4), datetime(2026, 1, 1, 10, 5), 3600))

  def test_skipped_full_refresh_is_caught_up(self):
    self.assertTrue(should_full_refresh(datetime(2026, 1, 1, 10, 6), datetime(2026, 1, 1, 9, 5), 3600))

  def test_initial_refresh_counts_as_full(self):
    self.assertFalse(should_full_refresh(datetime(2026, 1, 1, 10, 31), datetime(2026, 1, 1, 10, 30, 2), 3600))
    self.assertTrue(should_full_refresh(datetime(2026, 1, 1, 10, 31), None, 3600))

  def test_full_refresh_every_minute(self):
    self.assertTrue(should_full_refresh(datetime(2026, 1, 1, 10, 31), datetime(2026, 1, 1, 10, 30), 60))

  def test_full_refresh_slot_sub_minute(self):
    self.assertEqual(get_latest_full_refresh_slot(datetime(2026, 1, 1, 10, 31, 25, 500), 10), datetime(2026, 1, 1, 10, 31, 20))
    self.assertEqual(get_latest_full_refresh_slot(datetime(2026, 1, 1, 10, 0, 4), 15), datetime(2026, 1, 1, 10, 0, 0))
    self.assertFalse(should_full_refresh(datetime(2026, 1, 1, 10, 31, 29), datetime(2026, 1, 1, 10, 31, 20), 10))
    self.assertTrue(should_full_refresh(datetime(2026, 1, 1, 10, 31, 30), datetime(2026, 1, 1, 10, 31, 20), 10))


if __name__ == '__main__':
    unittest.main()
