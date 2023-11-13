#!/usr/bin/env python
# coding: utf-8
"""
ABM model test class
@author: iTzSte & hector@bith.net
"""
import unittest
from market_power.model import Model
from market_power.firm import Firm


class MarketPowerTest(unittest.TestCase):
    shocks = []
    model = None

    def configureTest(self, **kwargs):
        self.model = Model()
        self.model.test = True

        for key, value in kwargs.items():
            if hasattr(self.model.config, key):
                setattr(self.model.config, key, value)
            else:
                raise ValueError(f"config has not attr {key}={value}")
        self.model.config.__init__()
        self.model.log.define_log(log='DEBUG')
        self.model.initialize_model()

    def doTest(self):
        self.model.run()

    def __check_values__(self, firm, name, value):
        if value < 0:
            self.model.log.debug("******",
                                 f"{firm.getId()} value {name}={value} <0 is not valid: I changed it to 0")
            return 0
        else:
            return value

    def setFirm(self, firm: Firm, K: float, L: float, A: float):
        K = self.__check_values__(firm, 'K', K)
        A = self.__check_values__(firm, 'A', A)
        L = self.__check_values__(firm, 'L', L)
        if L + K != A:
            L = A - K
            self.model.log.debug("******",
                                 f"{firm.getId()} K must be equal to A+L => L modified to {L:.3f}")
        firm.L = L
        firm.A = A
        firm.K = K

    def assertFirm(self, firm: Firm, failures: int = None,
                   K: float = None, L: float = None, A: float = None):
        if L:
            self.assertEqual(firm.L, L)
        if K:
            self.assertEqual(firm.K, K)
        if A:
            self.assertEqual(firm.A, A)
        if failures:
            self.asserEqual(firm.failures, failures)
        if L and K and A:
            self.assertEqual(firm.K, firm.A+firm.L)

    def assertFirms(self, K: float = None, failures: int = None, L: float = None, A: float = None):
        self.model.statistics.current_status_save()
        if L:
            self.assertEqual(float(self.model.statistics.data["firmsL"][self.model.t]), L)
        if K:
            self.assertEqual(float(self.model.statistics.data["firmsK"][self.model.t]), K)
        if A:
            self.assertEqual(float(self.model.statistics.data["firmsA"][self.model.t]), A)
        if failures:
            self.asserEqual(float(self.model.statistics.data["failures"][self.model.t]), failures)
        if L and K and A:
            self.assertEqual(float(self.model.statistics.data["firmsK"][self.model.t]),
                             float(self.model.statistics.data["firmsL"][self.model.t])+
                             float(self.model.statistics.data["firmsA"][self.model.t]))

    def assertBankSector(self, D: float = None, L: float = None, A: float = None, credit_supply: float = None):
        if L:
            self.assertEqual(self.model.bank_sector.L, L)
        if D:
            self.assertEqual(self.model.bank_sector.D, D)
        if A:
            self.assertEqual(self.model.bank_sector.A, A)
        if credit_supply:
            self.assertEqual(self.model.bank_sector.credit_supply, credit_supply)
        if L and D and A:
            self.assertEqual(self.model.bank_sector.L, self.model.bank_sector.A+self.model.bank_sector.D)


