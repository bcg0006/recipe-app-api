"""This file contains the tests for the app."""

from django.test import SimpleTestCase
from app import calc


class CalcTest(SimpleTestCase):
    """Test the calc module"""

    def test_add(self):
        """Test the add function """
        self.assertEqual(calc.add(3, 8), 11)
        self.assertEqual(calc.add(-3, 8), 5)
        self.assertEqual(calc.add(-3, -8), -11)
        self.assertEqual(calc.add(3, -8), -5)


class SubstractNumbers(SimpleTestCase):
    """   Test the calc module  """

    def test_substract(self):
        """  Test the substract function """
        res = calc.subtract(5, 11)
        self.assertEqual(res, -6)
