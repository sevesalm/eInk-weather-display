import unittest
import celestial
from datetime import datetime
import pytz
import pprint

class TestCelestial(unittest.TestCase):
  HELSINKI_LOCATION = (60.192059, 24.945831)
  IVALO_LOCATION = (68.6576, 27.5397)
  QUAANAAK_LOCATION = (77.4670, -69.2285)
  MCMURDO_LOCATION = (-77.8419, 166.6863)
  MOUNT_ELLSWORTH_LOCATION = (-85.75, -161)
  pp = pprint.PrettyPrinter(indent=2)
  def test_get_nearest_sun_transit_prev(self):
    """
    Test that the method returns the previous sun transit.
    """
    now = datetime.fromisoformat('2021-12-28T00:21:00+02:00')
    (nearest_transit, _) = celestial.get_nearest_sun_transit(self.HELSINKI_LOCATION, now)
    self.assertEqual(nearest_transit.isoformat(), '2021-12-27T12:21:18.440452+02:00')

  def test_get_nearest_sun_transit_next(self):
    """
    Test that the method returns the previous sun transit.
    """
    now = datetime.fromisoformat('2021-12-28T00:22:00+02:00')
    (nearest_transit, _) = celestial.get_nearest_sun_transit(self.HELSINKI_LOCATION, now)
    self.assertEqual(nearest_transit.isoformat(), '2021-12-28T12:21:47.852356+02:00')

  def test_get_dusks_and_dawns_helsinki_winter_noon(self):
    now = datetime.fromisoformat('2021-12-21T12:00:00+02:00')
    result = celestial.get_dusks_and_dawns(self.HELSINKI_LOCATION, now)
    self.assertEqual(result["twilights"], [4,3,2,1,0,1,2,3,4])
    self.assertEqual(result["now_index"], 4)
 
  def test_get_dusks_and_dawns_helsinki_winter_nautical_dusk(self):
    now = datetime.fromisoformat('2021-12-21T16:30:00+02:00')
    result = celestial.get_dusks_and_dawns(self.HELSINKI_LOCATION, now)
    self.assertEqual(result["twilights"], [4,3,2,1,0,1,2,3,4])
    self.assertEqual(result["now_index"], 6)

  def test_get_dusks_and_dawns_helsinki(self):
    now = datetime.fromisoformat('2021-08-21T12:00:00+02:00')
    result = celestial.get_dusks_and_dawns(self.HELSINKI_LOCATION, now)
    self.assertEqual(result["twilights"], [3,2,1,0,1,2,3,4])

  def test_get_dusks_and_dawns_ivalo_winter(self):
    now = datetime.fromisoformat('2021-12-04T12:00:00+02:00')
    result = celestial.get_dusks_and_dawns(self.IVALO_LOCATION, now)
    self.assertEqual(result["twilights"], [4,3,2,1,2,3,4])

  def test_get_dusks_and_dawns_ivalo_summer(self):
    now = datetime.fromisoformat('2021-06-01T12:00:00+02:00')
    result = celestial.get_dusks_and_dawns(self.IVALO_LOCATION, now)
    self.assertEqual(result["twilights"], [0])
    self.assertEqual(result["now_index"], 0)

  def test_get_dusks_and_dawns_ivalo_spring(self):
    now = datetime.fromisoformat('2021-04-01T12:00:00+02:00')
    result = celestial.get_dusks_and_dawns(self.IVALO_LOCATION, now)
    self.assertEqual(result["twilights"], [3,2,1,0,1,2,3])

  def test_get_dusks_and_dawns_quaanaak_spring(self):
    now = datetime.fromisoformat('2021-03-06T12:00:00+02:00')
    result = celestial.get_dusks_and_dawns(self.QUAANAAK_LOCATION, now)
    self.assertEqual(result["twilights"], [4,3,2,1,0,1,2,3])

  def test_get_dusks_and_dawns_quaanaak_summer(self):
    now = datetime.fromisoformat('2021-06-01T12:00:00+02:00')
    result = celestial.get_dusks_and_dawns(self.MCMURDO_LOCATION, now)
    self.assertEqual(result["twilights"], [4,3,2,3,4])

  def test_get_dusks_and_dawns_mount_ellsworth_autumn(self):
    now = datetime.fromisoformat('2021-08-16T12:00:00+02:00')
    result = celestial.get_dusks_and_dawns(self.MOUNT_ELLSWORTH_LOCATION, now)
    self.assertEqual(result["twilights"], [4,3,2,3])

  def test_get_dusks_and_dawns_mount_ellsworth_summer(self):
    now = datetime.fromisoformat('2021-07-10T12:00:00+02:00')
    result = celestial.get_dusks_and_dawns(self.MOUNT_ELLSWORTH_LOCATION, now)
    self.assertEqual(result["twilights"], [4,3,4])

if __name__ == '__main__':
    unittest.main()
