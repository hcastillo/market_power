#!/usr/bin/env python
# coding: utf-8
"""
ABM model tests if the sums of values after execute current_status_save() are correct
"""
import unittest
from util.log import Log
from market_power.model import Model
from market_power.firm import Firm
from market_power.bank import BankSector
from util.stats_array import StatsFirms, StatsBankSector
from util.statistics import Statistics


class TestLog(unittest.TestCase):

    def setUp(self):
        self.model = Model(N=2, T=2, bank_sector_A_i0=20, firms_A_i0=2)
        self.log = Log(self.model)
        self.model.test = True
        self.statistics = Statistics(self.model)

        self.statistics.add(what="firms", name="K", prepend="*text*")
        self.statistics.add(what="firms", name="A")
        self.statistics.add(what="firms", name="L", logarithm=True)
        self.statistics.add(what="firms", name="Failures", symbol="$", attr_name="is_bankrupted", number_type=int)
        self.statistics.add(what="bank", name="L")
        self.model.config.__init__()

    def test_values(self):
        # before starting the execution, we have two firms and four items in statistics data
        self.assertEqual(self.model.firms[0].A, 2.0)
        self.assertEqual(self.model.firms[1].K, 5.0)
        self.assertEqual(self.model.firms[0].L, 3.0)
        self.assertEqual(len(self.model.firms), 2)
        self.assertEqual(len(self.statistics.data), 5)
        # check that the classes are in the correct order and the data stored with the correct names
        self.assertIsInstance(self.statistics.data['firms_A'], StatsFirms)
        self.assertIsInstance(self.statistics.data['bank_L'], StatsBankSector)

        result = self.statistics.current_status_save()
        # check that the data is correctly sum/stored:
        # sum firmA = 4
        # sum firmK = 10
        # sum firmL = ln(8) = (2,0794415416798359282516963643745)
        self.assertEqual(float(self.statistics.data['firms_A'][0]), 4.0)
        self.assertEqual(float(self.statistics.data['firms_K'][0]), 10.0)
        self.assertEqual(self.statistics.data['firms_L'][0], '  1.792')
        # string with the order of stored items and prepends / separators and symbols:
        self.assertEqual(result, '*text*ΣK= 10.000ΣA=  4.000ΣLΞ  1.792Σ$=   0L=250.000')


if __name__ == '__main__':
    unittest.main()
