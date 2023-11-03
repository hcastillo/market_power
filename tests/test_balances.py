#!/usr/bin/env python
# coding: utf-8
"""
ABM model test to check if we have 10 firms, the bankSector has the correct initial parameters
@author: iTzSte & hector@bith.net
"""
import unittest
import tests.market_power_testclass as testclass


class BalanceAtCreationTestCase(testclass.MarketPowerTest):

    def setUp(self):
        self.configureTest(N=10, T=1)

    def test_values(self):
        self.assertFirms(failures=0, K=50, A=10, L=40)
        self.assertFirm(self.model.firms[0], K=5, A=1, L=4)
        self.assertBankSector(A=3.2, L=40, D=36.8)
        # by default, we assure 8% of L as A
        #   100 firms with firm.L0 = 4 -> bank.A=32, bank.D = 368
        #   10  firms                4 -> bank.A=3.2 -> bank.D= 36.8

if __name__ == '__main__':
    unittest.main()
