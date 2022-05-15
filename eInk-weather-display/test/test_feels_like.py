import unittest
from feels_like_temperature import get_temp_chill, get_temp_heat, get_d_temp_sun


class TestCelestial(unittest.TestCase):
  def test_get_temp_chill_1(self):
    temp_chill = get_temp_chill(-10, 0)
    self.assertAlmostEqual(temp_chill, -10)

  def test_get_temp_chill_2(self):
    temp_chill = get_temp_chill(-10, 10)
    self.assertAlmostEqual(temp_chill, -18.9, places=1)

  def test_get_temp_chill_3(self):
    temp_chill = get_temp_chill(-2, 10)
    self.assertAlmostEqual(temp_chill, -9.4, places=1)

  def test_get_temp_heat_1(self):
    temp_heat = get_temp_heat(10, 0.1)
    self.assertAlmostEqual(temp_heat, 10, places=1)

  def test_get_temp_heat_2(self):
    temp_heat = get_temp_heat(10, 0.9)
    self.assertAlmostEqual(temp_heat, 10, places=1)

  def test_get_temp_heat_3(self):
    temp_heat = get_temp_heat(30, 0.9)
    self.assertAlmostEqual(temp_heat, 34.7, places=1)

  def test_get_d_temp_sun_1(self):
    d_temp_sun = get_d_temp_sun(50, 0)
    self.assertAlmostEqual(d_temp_sun, 0, places=1)

  def test_get_d_temp_sun_2(self):
    d_temp_sun = get_d_temp_sun(250, 0)
    self.assertAlmostEqual(d_temp_sun, 0.98, places=1)

  def test_get_d_temp_sun_3(self):
    d_temp_sun = get_d_temp_sun(250, 15)
    self.assertAlmostEqual(d_temp_sun, 0.2, places=1)


if __name__ == '__main__':
    unittest.main()
