#!/usr/bin/env python
# coding: utf-8
"""
ABM model

@author: hector@bith.net
"""


class BankSector:
    def __init__(self, its_model):
        self.model = its_model
        self.bad_debt = self.profits = self.totalA = self.totalK = 0.0
        self.A = self.model.config.bank_sector_A_i0
        self.L = self.model.config.bank_sector_L_i0
        self.D = self.determine_deposits()
        self.credit_supply = self.determine_new_credit_suppy()
        self.set_total_A_K()

    def determine_deposits(self):
        # L = A + D, ----> D = L-A
        return self.L - self.A

    def determine_profits(self):
        # (Equation 34)
        profits_loans = 0.0
        for firm in self.model.firms:
            profits_loans += firm.r * firm.L

        remunerations_of_deposits_and_networth = self.determine_average_interest_rate() * (self.D + self.A)

        return profits_loans - remunerations_of_deposits_and_networth


    def determine_average_interest_rate(self):
        return 0.01
        # TODO r = 0
        # for firm in self.model.firms:
        #    r += firm.r
        # avg_r = r / len(self.model.firms)
        # return avg_r if avg_r > self.model.config.r_i0 else self.model.config.r_i0

    def determine_equity(self):
        # (Equation 35) At = At-1 + profits - bad_debt
        return self.A + self.profits - self.bad_debt

    def __str__(self):
        return f"bankSector L={self.model.log.format(self.L)} A={self.model.log.format(self.A)} " + \
            f"D={self.model.log.format(self.D)} cs={self.model.log.format(self.credit_supply)}"

    def determine_step_results(self):
        self.profits = self.determine_profits()
        self.A = self.determine_equity()
        self.L = self.credit_supply
        self.D = self.determine_deposits()
        self.credit_supply = self.determine_new_credit_suppy()

    def determine_firm_capacity_loan(self, firm):
        # (Equation 11 of paper a new approach to business fluctuations)
        return (self.model.config.lambda_param * self.credit_supply * firm.K / self.totalK +
                (1 - self.model.config.lambda_param) * self.credit_supply * firm.A / self.totalA)

    def determine_new_credit_suppy(self):
        return self.A / self.model.config.alpha

    def add_bad_debt(self, amount):
        self.bad_debt += amount

    def set_total_A_K(self):
        self.totalA = sum(float(firm.A) for firm in self.model.firms)
        self.totalK = sum(float(firm.K) for firm in self.model.firms)
