#!/usr/bin/env python
# coding: utf-8
"""
ABM model

@author: hector@bith.net
"""


class BankSector:
    def __init__(self, its_model, A_i0=None):
        self.model = its_model
        self.bad_debt = self.profits = self.totalA = self.totalK = 0.0
        self.A = A_i0 if A_i0 else self.model.config.bank_sector_A_i0
        self.L = self.A / self.model.config.alpha
        self.D = self.L - self.A
        if self.D < 0:
            raise ValueError("error bank.D<0 due to " +
                             f"D=L-A={self.model.log.format(self.L)}-{self.model.log.format(self.A)}")
        self.credit_supply = self.determine_new_credit_suppy()
        self.estimate_total_A_K()

    def determine_deposits(self):
        # L = A + D, ----> D = L-A
        return self.L - self.A

    def determine_profits(self):
        # (Equation 34)
        profits_loans = 0.0
        for firm in self.model.firms:
            profits_loans += firm.r * firm.L

        #TODO 0.02 always instead of average interest rate for determine remunerations
        #remunerations_of_deposits_and_networth = 0.02 * (self.D + self.A)
        remunerations_of_deposits_and_networth = self.determine_average_interest_rate() * (self.D + self.A)

        return profits_loans - remunerations_of_deposits_and_networth

    def determine_average_interest_rate(self):
        #avg_r = sum(firm.r for firm in self.model.firms) / len(self.model.firms)
        #return avg_r if avg_r > self.model.config.r_i0 else self.model.config.r_i0
        return 0.00 #TODO

    def determine_equity(self):
        # (Equation 35) At = At-1 + profits - bad_debt
        return self.A + self.profits - self.bad_debt

    def __str__(self):
        return f"bankSector L={self.model.log.format(self.L)} A={self.model.log.format(self.A)} " + \
            f"D={self.model.log.format(self.D)} cs={self.model.log.format(self.credit_supply)}"

    def determine_step_results(self):
        self.profits = self.determine_profits()
        self.L = self.A / self.model.config.alpha
        self.A = self.determine_equity()
        # self.L = self.credit_supply
        self.D = self.determine_deposits()
        self.credit_supply = self.determine_new_credit_suppy()

    def determine_firm_capacity_loan(self, firm):
        # (Equation 11 of paper a new approach to business fluctuations)
        offeredL = (self.model.config.lambda_param * self.credit_supply * firm.K / self.totalK +
                    (1 - self.model.config.lambda_param) * self.credit_supply * firm.A / self.totalA)
        if offeredL < 0:
            offeredL = firm.L #TODO innecesary?
        self.model.log.debug(f"{firm} offeredL={offeredL}")
        return offeredL

    def determine_new_credit_suppy(self):
        return self.A / self.model.config.alpha

    def add_bad_debt(self, amount):
        self.bad_debt += amount

    def estimate_total_A_K(self):
        self.totalA = sum(float(firm.A) for firm in self.model.firms)
        self.totalK = sum(float(firm.K) for firm in self.model.firms)
