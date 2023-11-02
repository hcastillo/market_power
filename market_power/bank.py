#!/usr/bin/env python
# coding: utf-8
"""
ABM model

@author: hector@bith.net
"""


class BankSector:
    def __init__(self, its_model):
        self.model = its_model
        self.credit_supply = 0.0
        self.bad_debt = 0.0
        self.profits = 0.0
        self.A = self.model.config.bank_sector_A_i0
        self.L = self.model.config.bank_sector_L_i0
        self.D = self.determine_deposits()

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
        r = 0
        for firm in self.model.firms:
            r += firm.r
        avg_r = r / len(self.model.firms)
        return avg_r if avg_r > self.model.config.r_i0 else self.model.config.r_i0

    def determine_equity(self):
        # (Equation 35) At = At-1 + profits - bad_debt
        return self.A + self.profits - self.bad_debt

    def determine_loans(self):
        return sum(float(firm.L) for firm in self.model.firms)

    def __str__(self):
        return f"bankSector L={self.L:8.3} A={self.A:8.3} D={self.D:8.3}"

    def determine_step_results(self):
        self.A = self.determine_equity()
        self.L = self.determine_loans()
        self.D = self.determine_deposits()
        self.profits = self.determine_profits()

    def determine_capacity_loan(self, firm):
        # (Equation 11 of paper a new approach to business fluctuations)
        totalA = sum(float(firm.A) for firm in self.model.firms)
        totalK= sum(float(firm.K) for firm in self.model.firms)
        return (self.model.config.lambda_param * self.credit_supply * firm.K / totalK +
                (1 - self.model.config.lambda_param) * self.credit_supply * firm.A / totalA )

    def set_new_credit_suppy(self):
        self.credit_supply = self.A / self.model.config.alpha
        self.model.log.debug(f"new credit supply is {self.model.log.format(self.credit_supply)}")

    def add_bad_debt(self, amount):
        self.bad_debt += amount