#!/usr/bin/env python
# coding: utf-8
"""
ABM model

@author: hector@bith.net
"""
import random


class Firm:
    def __init__(self, new_id, its_model):
        self.id = new_id
        self.model = its_model
        self.failures = 0
        self.__assign_defaults__()

    def __str__(self, short: bool = False):
        init = "firm#" if not short else "#"
        if self.failures > 0:
            return f"{init}{self.id}.{self.failures:<2}"
        else:
            return f"{init}{self.id}   "

    def __assign_defaults__(self):
        self.K = self.model.config.firms_K_i0
        self.A = self.model.config.firms_A_i0
        self.L = self.model.config.firms_L_i0
        self.r = self.model.config.r_i0
        self.gamma = self.model.config.gamma
        self.phi = self.model.config.phi
        self.pi = 0.0
        self.Y = 0.0
        self.desiredK = self.desiredL = self.obtainedL = 0.0

    def do_step(self):
        self.gamma = self.determine_cost_per_unit_of_capital()
        self.c = self.determine_marginal_operating_cost()
        self.Y = self.determine_output()
        # self.Pb     = self.determine_prob_bankruptcy()
        self.pi = self.determine_profits()
        self.r = self.determine_interest_rate()
        self.desiredK = self.determine_desired_capital()
        self.I = self.determine_investment()

        self.desiredL = self.determine_new_loan()
        self.obtainedL = self.model.bank_sector.determine_capacity_loan(self)
        if self.desiredL > self.obtainedL:
            self.A -= (self.desiredL - self.obtainedL)
            self.L += self.obtainedL
        else:
            self.L += self.desiredL
        self.balance_firm()
        self.phi = self.determine_phi()

    def determine_cost_per_unit_of_capital(self):
        # (Before equation 2)  gamma
        return (self.model.config.w / self.model.config.k) + (self.model.config.g * self.r)

    def determine_marginal_operating_cost(self):
        # (Equation 2)
        return self.gamma / self.phi

    # def determine_prob_bankruptcy(self):
    #     # (Equation 10) Pb
    #     return (1 / (2 * (1 - self.model.config.sigma) * (1 - self.model.config.eta))) * (
    #             (self.gamma / self.phi) - (self.A / self.output))

    def determine_interest_rate(self):
        # (Equation 33)
        return self.model.config.beta * self.L / self.A

    def lack_of_loan_gap(self, gap):
        self.A -= gap

    def determine_desired_capital(self):
        # (Equation 22)
        return (1 - self.model.config.eta) ** 2 / (self.model.config.b * self.gamma) - \
            (1 - self.model.config.eta) / (self.model.config.b * self.phi) + \
            self.A / (2 * self.gamma)

    def determine_investment(self):
        # (Below equation 33)
        return self.desiredK - self.K

    def determine_new_loan(self):
        # (Over equation 33)
        return self.L + (1 + self.model.config.m) * self.I - self.pi

    def u(self):
        # stochastic demand [0,2]
        return random.uniform(0, 2)

    def determine_output(self):
        # (Equation 21)
        return (1 - self.model.config.eta) ** 2 * self.phi / (self.model.config.b * self.gamma) - \
            (1 - self.model.config.eta) / self.model.config.b + \
            self.phi / (2 * self.gamma) * self.A

    def determine_profits(self):
        # (Equation 24)
        return self.u() * (self.model.config.eta + (1 - self.model.config.eta) * self.Y) - \
                 self.c * self.Y

    def determine_assets(self):
        # (Equation 8)
        return self.A + self.pi

    def determine_phi(self):
        return self.phi

    def check_loses_are_covered_by_m(self):
        return (self.pi < 0) and (self.K * self.model.config.m + self.pi) >= 0

    def is_bankrupted(self):
        return (self.A + self.pi) < 0

    def set_failed(self):
        self.failures += 1
        self.__assign_defaults__()

    def balance_firm(self):
        if self.L < 0:
            self.L = 0.0
        # balance sheet adjustment
        if self.pi >= 0:
            if self.K < (self.A + self.L):
                self.K = (self.A + self.L)
        else:
            if self.K > (self.A + self.L):
                self.K = (self.A + self.L)
        if self.A+self.L<self.K:
            self.A = self.K - self.L