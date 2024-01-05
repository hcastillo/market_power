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
        self.configureTest(N=10, T=1, bank_sector_A_i0=5)
        self.model.statistics.add(what="firms", name="K", logarithm=True)
        self.model.statistics.add(what="firms", name="A")
        self.model.statistics.add(what="firms", name="L", logarithm=True)
        self.model.statistics.add(what="firms", name="failures", attr_name="failed", symbol="fail",
                                  number_type=int)

    def test_values(self):
        # without log : self.assertFirms(failures=0, K=50, A=10, L=40)
        # with log:
        self.assertFirms(failures=0, K=3.912023005428146, A=10, L=3.6888794541139363)
        self.assertFirm(self.model.firms[0], K=5, A=1, L=4)

        self.assertBankSector(A=5, L=62.5, D=57.5)  # (A=5, L=62.5, D=57.5)
        # by default initially bank.L = bank.cs = firm.L*N
        #            after first step, cs=bank.A/alpha
        #    bank.A=5, bank.L=4/0.08=62.5, bank.D=57.5

        self.doTest()
        self.assertBankSector(A=-6.368770257540131, D=-73.2408579617115, L=-79.60962821925163)


if __name__ == '__main__':
    unittest.main()
