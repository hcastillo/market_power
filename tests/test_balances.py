#!/usr/bin/env python
# coding: utf-8
"""
ABM model test to check if we have 10 firms, the bankSector has the correct initial parameters
@author: iTzSte & hector@bith.net
"""
import unittest
import tests.market_power_testclass as test_class


class BalanceAtCreationTestCase(test_class.MarketPowerTest):

    def setUp(self):
        self.configureTest(N=10, T=1, bank_sector_A_i0=5, firms_L_i0=4)

    def test_values(self):
        self.assertFirms(failures=0, K=50, A=10, L=40)
        self.assertFirm(self.model.firms[0], K=5, A=1, L=4)

        self.assertBankSector(A=5, L=40, D=35, credit_supply=40)
        # by default initially bank.L = bank.cs = firm.L*N
        #            after first step, cs=bank.A/alpha
        #    bank.A=5, bank.L=4/0.08=62.5, bank.D=57.5

        self.doTest()
        self.assertBankSector(A=-562.2805682060567, L=40, D=-522.2805682060567, credit_supply=7028.507102575709)


if __name__ == '__main__':
    unittest.main()
