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
        self.cs = 0

    def determine_deposits(self):
        return self.L - self.A

    def determine_profits(self):
        # (Equation 34)
        profits = 0.0
        for firm in self.model.firms:
            if not firm.failed:
                profits += firm.r * firm.L
        avg_r = self.determine_average_interest_rate()
        profits -= avg_r*(self.D + self.A)
        return profits


    def determine_average_interest_rate(self):
        r = 0
        num_firms = 0
        for firm in self.model.firms:
            if not firm.failed:
                num_firms += 1
                r += firm.r
        return r/num_firms

    def determine_equity(self):
        # (Equation 35)
        return self.A + self.profits - self.BD

    def __str__(self):
        return f"bankSector"

    def do_step(self):
        self.profits = self.determine_profits()
        self.A = self.determine_equity()
        self.D = self.determine_deposits()
        self.BD = 0

    def __assign_defaults__(self):
        self.A = self.model.config.bank_sector_A_i0
        self.L = self.model.config.bank_sector_L_i0
        self.D = self.model.config.bank_sector_D_i0
        self.BD = 0.0

    def bankrupted_firm(self, amount_lost_L):
        self.BD += amount_lost_L

    def determine_capacity_loan(self, firm_A):
        capacity = firm_A / self.A * 100
        self.cs -= capacity
        if self.cs < 0:
            capacity += self.cs
        return capacity

    def determine_new_step_credit_suppy(self):
        return self.A / self.model.config.alfa
