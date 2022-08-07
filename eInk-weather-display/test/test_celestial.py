import unittest
import celestial
from datetime import datetime, timedelta
import pprint


class TestCelestial(unittest.TestCase):
  HELSINKI_LOCATION = ('60.192059', '24.945831')
  IVALO_LOCATION = ('68.6576', '27.5397')
  QUAANAAK_LOCATION = ('77.4670', '-69.2285')
  MCMURDO_LOCATION = ('-77.8419', '166.6863')
  MOUNT_ELLSWORTH_LOCATION = ('-85.75', '-161')
  pp = pprint.PrettyPrinter(indent=2)

  @unittest.skip("Does not currently work on CI")
  def test_get_nearest_sun_transit_prev(self):
    """
    Test that the method returns the previous sun transit.
    """
    now = datetime.fromisoformat('2021-12-28T00:21:00+02:00')
    (nearest_transit, _) = celestial.get_nearest_sun_transit(self.HELSINKI_LOCATION, now)
    self.assertEqual(nearest_transit.isoformat(), '2021-12-27T12:21:18.435578+02:00')

  @unittest.skip("Does not currently work on CI")
  def test_get_nearest_sun_transit_next(self):
    """
    Test that the method returns the previous sun transit.
    """
    now = datetime.fromisoformat('2021-12-28T00:22:00+02:00')
    (nearest_transit, _) = celestial.get_nearest_sun_transit(self.HELSINKI_LOCATION, now)
    self.assertEqual(nearest_transit.isoformat(), '2021-12-28T12:21:47.847482+02:00')

  def test_get_dusks_and_dawns_helsinki_winter_noon(self):
    now = datetime.fromisoformat('2021-12-21T12:00:00+02:00')
    result = celestial.get_dusks_and_dawns(self.HELSINKI_LOCATION, now)
    self.assertEqual(result["twilights"], [4, 3, 2, 1, 0, 1, 2, 3, 4])
    self.assertEqual(result["now_index"], 4)

  def test_get_dusks_and_dawns_helsinki_winter_nautical_dusk(self):
    now = datetime.fromisoformat('2021-12-21T16:30:00+02:00')
    result = celestial.get_dusks_and_dawns(self.HELSINKI_LOCATION, now)
    self.assertEqual(result["twilights"], [4, 3, 2, 1, 0, 1, 2, 3, 4])
    self.assertEqual(result["now_index"], 6)

  def test_get_dusks_and_dawns_helsinki(self):
    now = datetime.fromisoformat('2021-08-21T12:00:00+02:00')
    result = celestial.get_dusks_and_dawns(self.HELSINKI_LOCATION, now)
    self.assertEqual(result["twilights"], [3, 2, 1, 0, 1, 2, 3, 4])

  def test_get_dusks_and_dawns_ivalo_winter(self):
    now = datetime.fromisoformat('2021-12-04T12:00:00+02:00')
    result = celestial.get_dusks_and_dawns(self.IVALO_LOCATION, now)
    self.assertEqual(result["twilights"], [4, 3, 2, 1, 2, 3, 4])

  def test_get_dusks_and_dawns_ivalo_summer(self):
    now = datetime.fromisoformat('2021-06-01T12:00:00+02:00')
    result = celestial.get_dusks_and_dawns(self.IVALO_LOCATION, now)
    self.assertEqual(result["twilights"], [0])
    self.assertEqual(result["now_index"], 0)

  def test_get_dusks_and_dawns_ivalo_spring(self):
    now = datetime.fromisoformat('2021-04-01T12:00:00+02:00')
    result = celestial.get_dusks_and_dawns(self.IVALO_LOCATION, now)
    self.assertEqual(result["twilights"], [3, 2, 1, 0, 1, 2, 3])

  def test_get_dusks_and_dawns_quaanaak_spring(self):
    now = datetime.fromisoformat('2021-03-06T12:00:00+02:00')
    result = celestial.get_dusks_and_dawns(self.QUAANAAK_LOCATION, now)
    self.assertEqual(result["twilights"], [4, 3, 2, 1, 0, 1, 2, 3])

  def test_get_dusks_and_dawns_quaanaak_summer(self):
    now = datetime.fromisoformat('2021-06-01T12:00:00+02:00')
    result = celestial.get_dusks_and_dawns(self.MCMURDO_LOCATION, now)
    self.assertEqual(result["twilights"], [4, 3, 2, 3, 4])

  def test_get_dusks_and_dawns_mount_ellsworth_autumn(self):
    now = datetime.fromisoformat('2021-08-16T12:00:00+02:00')
    result = celestial.get_dusks_and_dawns(self.MOUNT_ELLSWORTH_LOCATION, now)
    self.assertEqual(result["twilights"], [4, 3, 2, 3])

  def test_get_dusks_and_dawns_mount_ellsworth_summer(self):
    now = datetime.fromisoformat('2021-07-10T12:00:00+02:00')
    result = celestial.get_dusks_and_dawns(self.MOUNT_ELLSWORTH_LOCATION, now)
    self.assertEqual(result["twilights"], [4, 3, 4])

  def test_get_twilight_length_helsinki_summer(self):
    expected = timedelta(hours=15, minutes=9, seconds=13.1).total_seconds()
    now = datetime.fromisoformat('2021-08-21T12:00:00+02:00')
    twilight_data = celestial.get_dusks_and_dawns(self.HELSINKI_LOCATION, now)
    result = celestial.get_twilight_length(twilight_data, 3).total_seconds()
    self.assertAlmostEqual(result, expected, delta=1)

  def test_get_daytime_length_helsinki_summer(self):
    now = datetime.fromisoformat('2021-08-21T12:00:00+02:00')
    twilight_data = celestial.get_dusks_and_dawns(self.HELSINKI_LOCATION, now)
    daytime_length = celestial.get_daytime_length(twilight_data)
    self.assertIsNotNone(daytime_length)
    if (daytime_length is not None):
      daytime_length_seconds = daytime_length.total_seconds()
      twilight_length = celestial.get_twilight_length(twilight_data, 3).total_seconds()
      self.assertEqual(twilight_length, daytime_length_seconds)

  def test_get_twilight_length_helsinki_summer_with_exception(self):
    now = datetime.fromisoformat('2021-08-21T12:00:00+02:00')
    twilight_data = celestial.get_dusks_and_dawns(self.HELSINKI_LOCATION, now)
    self.assertRaises(Exception, celestial.get_twilight_length, twilight_data, 0)

  def test_get_twilight_length_mount_ellsworth_summer(self):
    expected = timedelta(minutes=33, seconds=55.6).total_seconds()
    now = datetime.fromisoformat('2021-07-10T12:00:00+02:00')
    twilight_data = celestial.get_dusks_and_dawns(self.MOUNT_ELLSWORTH_LOCATION, now)
    result = celestial.get_twilight_length(twilight_data, 1).total_seconds()
    self.assertAlmostEqual(result, expected, delta=1)

  def test_get_daytime_length_mount_ellsworth_summer(self):
    now = datetime.fromisoformat('2021-07-10T12:00:00+02:00')
    twilight_data = celestial.get_dusks_and_dawns(self.MOUNT_ELLSWORTH_LOCATION, now)
    result = celestial.get_daytime_length(twilight_data)
    self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
