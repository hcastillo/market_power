#!/usr/bin/env python
# coding: utf-8
"""
ABM model tests to check if we have 10 firms, the bankSector has the correct initial parameters
@author: iTzSte & hector@bith.net
"""
import unittest
import tests.market_power_testclass as test_class


class BalanceAtCreationTestCase(test_class.MarketPowerTest):

    def setUp(self):
        self.configureTest(N=10, T=1, bank_sector_A_i0=5, firms_L_i0=4)

    def test_values(self):
        self.assertRaises(LookupError, self.configureTest, noexist=True)
        self.assertRaises(ValueError, self.configureTest, N=0.02)
        self.assertRaises(ValueError, self.configureTest, alpha="a")

if __name__ == '__main__':
    unittest.main()
