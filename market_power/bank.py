#!/usr/bin/env python
# coding: utf-8
"""
ABM model

@author: hector@bith.net
"""


class BankSector:
    def __init__(self, its_model):
        self.model = its_model
        self.__assign_defaults__()
        # TODO  ste


    def determineDeposits(self):
        return self.L - self.A


    def determineProfits(self):
        profits = 0.0
        for firm in self.model.firms:
            profits += (((1 - firm.pb) * (firm.r * firm.L)) + (firm.pb * (self.model.config.teta * firm.A) - firm.L))
        return profits


    def determineEquity(self):
        return self.A + self.profits - self.B

    def __str__(self):
        return f"bankSector"


    def do_step(self):
        self.profits = self.determineProfits()
        self.A = self.determineEquity()
        self.D = self.determineDeposits()

    def __assign_defaults__(self):
        self.A = self.model.config.bank_sector_A_i0
        self.L = self.model.config.bank_sector_L_i0
        self.D = self.model.config.bank_sector_D_i0
        self.B = self.model.config.bank_sector_B_i0
        self.profits = self.model.config.bank_sector_profits
        self.cs = self.A / self.model.config.alfa

    def determineCreditSupply(self):
        return self.A / self.model.config.alfa
