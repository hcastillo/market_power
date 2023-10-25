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
        self.pb = 0.0
        self.profits = 0.0
        self.dK = 0.0
        self.phi = self.model.config.phi
        self.I = 0.0
        self.u = 0.0
        self.output = 0.0
        self.z = 0.0  # amount of R&D invested by the firm
        self.Z = 0.0  # Bernoulli's distribution parameter
        self.success = 0.0  # if the Bernoulli's parameter is 1, success is 1
        self.failed = False

    def do_step(self):
        self.gamma = self.determine_cost_per_unit_of_capital()
        self.c = self.determine_marginal_operating_cost()
        self.output = self.determineOutput()
        self.pb = self.determine_prob_bankruptcy()
        self.r = self.determineInterestRate()
        self.dK = self.determineDesiredCapital()
        if self.dK < (self.model.config.share_k * self.K):  # first control to have a minimum amount of dK
            self.dK = self.model.config.share_k * self.K
        if self.dK < 0:  # second control to avoid a negative dK
            self.dK = (self.model.config.firms_K_i0 / 2)
        self.I = self.determineInvestment()
        self.L = self.determineLoan()
        if self.L < 0:  # control to avoid negative loans
            self.A = self.A + abs(self.L)  # balance sheet adjustment
            self.L = 0
        if (self.A + self.L) > self.dK:  # first control for the balance sheet
            self.dK = (self.A + self.L)
        else:
            self.dK = (self.A + self.L)
        # TODO: we need to introduce a control by which: if the bank can provide the loan, dK becomes official K; \
        #  otherwise the firm should produce with the capital at its disposal, and the desired capital is useless
        self.u = self.determineU()
        self.profits = self.determineProfits()
        self.A = self.determineAssets()
        if self.profits >= 0:
            if self.K < (self.A + self.L):  # balance sheet adjustment
                self.K = (self.A + self.L)
        else:
            if self.K > (self.A + self.L):
                self.K = (self.A + self.L)
        self.z = self.determine_z()
        self.Z = self.determineZ()
        if self.Z == 1:  # I should verify this formula
            self.success = 1
        else:
            self.success = 0
        self.phi = self.determinePhi()

        if self.A < self.c * self.output:
            # ask for a loan to the banksector
            # TODO : I need to check it with Gabriele because I have never used it
            pass

    def determine_cost_per_unit_of_capital(self):
        # (Before equation 2)  gamma
        # TODO: w is uniform across firms, but not fixed for all t!     # we should talk with Gabriele
        return (self.model.config.w / self.model.config.k) + (self.model.config.g * self.r)

    def determine_marginal_operating_cost(self):
        # (Equation 2)
        return self.gamma / self.phi

    def determine_prob_bankruptcy(self):
        # (Equation 9S or Equation 10H) Pb
        return (1 / (2 * (1 - self.model.config.sigma) * (1 - self.model.config.eta))) * (
                (self.gamma / self.phi) - (self.A / self.output))

    def determineInterestRate(self):
        # new formula micro-founded
        return (self.pb / (1 - self.pb)) * self.model.config.mark_up_bank

    def determineDesiredCapital(self):
        # Equation 28 in my paper
        return ((1 - self.model.config.sigma) * (
                    ((1 - self.model.config.eta) ** 2 * (1 - self.model.config.sigma) * self.phi) - \
                    ((1 - self.model.config.eta) * self.gamma)) / (self.model.config.b * self.phi * self.gamma)) + \
            ((1 / (2 * self.gamma)) * self.A)

    def determineInvestment(self):
        # page 17 in my paper, in the Bank's chapter
        return self.dK - self.K

    def determineLoan(self):
        # page 17 in the bank's chapter
        return self.L + self.I - self.profits

    def determineU(self):
        return random.uniform(0, 2)

    def determineOutput(self):
        # (Before equation 2)
        # Y, output is equal to capital productivity * capital
        return self.K * self.phi

    def determineProfits(self):
        # (Equation 23 in my paper with R&D)
        return (self.u * (self.model.config.eta + ((1 - self.model.config.eta) * self.output)) * (
                    1 - self.model.config.sigma)) - \
            ((self.gamma / self.phi) * self.output)

    def determineAssets(self):
        return self.A + self.profits

    def determine_z(self):
        # page 16 of my paper : it calculates the amount of R&D invested by the firm
        # TODO: it should be verified
        return (self.u * (self.model.config.eta + ((1 - self.model.config.eta) * self.output)) * (
            self.model.config.sigma))

    def determineZ(self):
        # equation 29 of my paper
        return 1 - np.exp((- self.model.config.delta) * self.z)

    def determinePhi(self):
        if self.success == 1:
            self.phi = self.phi * (1 + self.model.config.xi)
        else:
            self.phi = self.phi
        return self.phi

    def determine_output(self):
        # (Before equation 2)
        # Y, output is equal to capital productivity * capital
        return self.K * self.phi
