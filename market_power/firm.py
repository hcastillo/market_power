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
        self.c = 0.2 #TODO
        self.desiredK = self.demandL = self.offeredL = 0.0
        self.gap_of_L = 0.0

    def do_step(self):
        self.gamma = self.determine_cost_per_unit_of_capital()
        self.desiredK = self.determine_desired_capital()
        self.I = self.determine_investment()
        self.demandL = self.determine_demand_loan()
        self.offeredL = self.model.bank_sector.determine_capacity_loan(self)

        if self.demandL > self.offeredL:
            self.gap_of_L = (self.demandL - self.offeredL)
            self.A -= self.gap_of_L
            self.K -= self.gap_of_L
            self.incrementL = self.offeredL
        else:
            self.gap_of_L = 0.0
            self.incrementL = self.demandL
        self.r = self.determine_interest_rate()
        self.pi = self.determine_profits()
        self.A = self.determine_worthnet()

        if self.is_bankrupted(): # A+pi<0
            self.set_failed()  # TODO increment BD in the bank etc etc
        else:
            self.L += self.incrementL
            self.K = self.adjust_capital()


    def determine_cost_per_unit_of_capital(self):
        # (Before equation 2)  gamma
        return (self.model.config.w / self.model.config.k) + (self.model.config.g * self.r)

    # def determine_marginal_operating_cost(self):
    #     # (Equation 2)
    #     return self.gamma / self.phi

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

    def determine_demand_loan(self):
        # (Over equation 33)
        return self.L + (1 + self.model.config.m) * self.I - self.pi

    def u(self):
        # stochastic demand [0,2]
        return random.uniform(0, 2)

    # def determine_output(self):
    #     # (Equation 21)
    #     return (1 - self.model.config.eta) ** 2 * self.phi / (self.model.config.b * self.gamma) - \
    #         (1 - self.model.config.eta) / self.model.config.b + \
    #         self.phi / (2 * self.gamma) * self.A

    def determine_profits(self):
        # (Equation 24)
        return self.u() * (self.model.config.eta + (1 - self.model.config.eta) * self.Y) - \
                 self.c * self.Y

    def determine_worthnet(self):
        # (Equation 8)
        return self.A + self.pi

    def determine_phi(self):
        return self.phi

    def check_loses_are_covered_by_m(self):
        return (self.pi < 0) and (self.K * self.model.config.m + self.pi) >= 0

    def is_bankrupted(self):
        return (self.A + self.pi) < 0

    def set_failed(self):
        if self.L - self.K < 0:
            self.model.bank_sector.add_bad_debt( self.K - self.L )
        self.failures += 1
        self.__assign_defaults__()

    def adjust_capital(self):
        if self.K < (self.A + self.L):
            self.model.log.debug(f"{self} K increased from {self.K} to {self.A + self.L}")
        if self.K > (self.A + self.L):
            self.model.log.debug(f"{self} K reduced from {self.K} to {self.A + self.L}")
        return (self.A + self.L)


