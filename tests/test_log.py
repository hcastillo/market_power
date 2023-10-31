#!/usr/bin/env python
# coding: utf-8
"""
ABM model test to check if we have 10 firms, the bankSector has the correct initial parameters
@author: iTzSte & hector@bith.net
"""
import unittest
from util.log import Log
from market_power.model import Model


class TestLog(unittest.TestCase):

    def setUp(self):
        self.log = Log(Model())

    def test_values(self):
        self.assertEqual(self.log.format(32)," 32")        # three characters for integer numbers
        self.assertEqual(self.log.format(2974),"2974")     # if more than three characters in integer
        self.assertEqual(self.log.format(0.0)," 0.00")     # 5 characters for real numbers (two decimals)
        self.assertEqual(self.log.format(974.0),"974.0")   # if decimal part is .0 then it's removed if size >1000
        self.assertEqual(self.log.format(2974.0)," 2974")  # if decimal part is .0 then it's removed if size >1000


if __name__ == '__main__':
    unittest.main()
