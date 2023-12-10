#!/usr/bin/env python
# coding: utf-8
"""
ABM model tests to verify the formats that the log.format() generate
@author: hector@bith.net
"""
import unittest
from util.log import Log
from market_power.model import Model


class TestLog(unittest.TestCase):

    def setUp(self):
        self.log = Log(Model())

    def test_values(self):
        self.assertEqual(self.log.format(32), "  32")
        self.assertEqual(self.log.format(2974), "2974")
        self.assertEqual(self.log.format(0.0), "  0.000")
        self.assertEqual(self.log.format(974.0), "974.000")
        self.assertEqual(self.log.format(2974.0), "2974.00")


if __name__ == '__main__':
    unittest.main()
