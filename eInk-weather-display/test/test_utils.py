import unittest
from utils import roundToString


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


if __name__ == '__main__':
    unittest.main()
