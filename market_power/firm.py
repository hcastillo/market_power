#!/usr/bin/env python
# coding: utf-8
"""
ABM model

@author: hector@bith.net
"""
import random
import numpy as np


class Firm:
    def __init__(self, new_id, its_model):
        self.id = new_id
        self.model = its_model
        self.failures = 0
        self.__assign_defaults__()

    def __str__(self, short: bool = False):
        init = "firm#" if not short else "#"
        if self.failures > 0:
            return f"{init}{self.id}.{self.failures}"
        else:
            return f"{init}{self.id}"

    def __assign_defaults__(self):
        self.K = self.model.config.firms_K_i0
        self.A = self.model.config.firms_A_i0
        self.L = self.model.config.firms_L_i0
        self.r = self.model.config.r
        self.gamma = self.model.config.gamma
        self.phi = self.model.config.phi

    def do_step(self):
        self.failed = False
        self.gamma = self.determine_cost_per_unit_of_capital()
        self.c = self.determine_marginal_operating_cost()
        self.output = self.determine_output()
        # self.Pb     = self.determine_prob_bankruptcy()
        self.profits = self.determine_profits()
        self.r = self.determine_interest_rate()
        self.dK = self.determine_desired_capital()
        self.I = self.determine_investment()

        if self.check_loses_are_covered_by_m():
            self.deplete_m()
        else:
            if self.check_loses_are_bankruptcy():
                self.model.bank_sector.bankrupted_firm(self.set_failed())

        if not self.failed:
            self.desiredL = self.determine_loan()
            self.obtainedL = self.model.bank_sector.determine_capacity_loan(self.A)
            if self.desiredL > self.obtainedL:
                self.lack_of_loan_gap(self.desiredL - self.obtainedL)
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
        return self.dK - self.K

    def determine_loan(self):
        # (Over equation 33)
        return self.L + (1 + self.model.config.m) * self.I - self.profits

    def u(self):
        return random.random()

    def determine_output(self):
        # (Equation 21)
        return (1 - self.model.config.eta) ** 2 * self.phi / (self.model.config.b * self.gamma) - \
            (1 - self.model.config.eta) / self.model.config.b + \
            self.phi / (2 * self.gamma) * self.A

    def determine_profits(self):
        # (Equation 5)
        return self.u() * self.output ** (1 - self.model.config.eta) - self.c * self.output

    def determine_assets(self):
        # (Equation 8)
        return self.A + self.profits

    def determine_phi(self):
        return self.phi

    def determine_output(self):
        # (Before equation 2)
        # Y, output is equal to capital productivity * capital
        return self.K * self.phi

    def check_loses_are_covered_by_m(self):
        return self.profits < 0 and (-self.profits) <= self.A

    def check_loses_are_bankruptcy(self):
        return self.profits < 0 and (-self.profits) <= self.A

    def deplete_m(self):
        # profits are loses (so they are negative)
        self.K += self.profits

    def set_failed(self):
        self.failed = True
        return self.K

    def execute_bankruptcy(self):
        if self.failed:
            self.failed = False
            self.failures += 1
            self.__assign_defaults__()

    def balance_firm(self):
        # balance sheet adjustment
        if self.profits >= 0:
            if self.K < (self.A + self.L):
                self.K = (self.A + self.L)
        else:
            if self.K > (self.A + self.L):
                self.K = (self.A + self.L)
