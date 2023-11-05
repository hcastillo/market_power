#!/usr/bin/env python
# coding: utf-8
"""
ABM model

@author: hector@bith.net
"""
import random


class Firm:
    def __init__(self, new_id=None, its_model=None):
        if its_model:
            self.id = new_id
            self.model = its_model
            self.failures = 0
            self.gamma = self.model.config.gamma
            self.debug_info = ""
        self.K = self.model.config.firms_K_i0
        self.A = self.model.config.firms_A_i0
        self.L = self.model.config.firms_L_i0
        self.r = self.model.config.r_i0
        self.gamma = self.model.config.gamma
        self.phi = self.model.config.phi
        self.pi = 0.0
        self.c = 0.0
        self.desiredK = self.demandL = self.offeredL = self.I = 0.0

    def __str__(self, short: bool = False):
        init = "firm#" if not short else "#"
        if self.failures > 0:
            return f"{init}{self.id}.{self.failures:<2}"
        else:
            return f"{init}{self.id}   "

    def do_step(self):
        self.debug_info = ""
        self.gamma = self.determine_cost_per_unit_of_capital()
        self.desiredK = self.determine_desired_capital()
        self.I = self.determine_investment()
        self.demandL = self.determine_demand_loan()
        self.offeredL = self.model.bank_sector.determine_firm_capacity_loan(self)

        if self.demandL > self.offeredL:
            gap_of_L = (self.demandL - self.offeredL)
            # self.A -= gap_of_L
            self.K -= gap_of_L
            self.debug_info += f"gapL={self.model.log.format(gap_of_L)} "
            self.L += self.offeredL
        else:
            self.L += self.demandL
        self.r = self.determine_interest_rate()
        self.c = self.determine_marginal_operating_cost()
        self.pi = self.determine_profits()
        self.A = self.determine_net_worth()

    def determine_cost_per_unit_of_capital(self):
        # (Before equation 2)  gamma
        return (self.model.config.w / self.model.config.k) + (self.model.config.g * self.r)

    def determine_marginal_operating_cost(self):
        # (Equation 2)
        return self.gamma / self.phi

    def determine_interest_rate(self):
        # (Equation 33)
        return self.model.config.beta * self.L / self.A

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

    def determine_profits(self):
        # (Equation 24)  , but with Y = phi*K
        return self.u() * (self.model.config.eta + (1 - self.model.config.eta) * self.phi * self.K) - \
            self.c * self.phi * self.K

    def determine_net_worth(self):
        # (Equation 8)
        return self.A + self.pi

    def check_loses_are_covered_by_m(self):
        return (self.pi < 0) and (self.K * self.model.config.m + self.pi) >= 0

    def is_bankrupted(self):
        return self.A < self.model.config.threshold_bankrupt or self.debug_info.find("failed") > 0

    def set_failed(self):
        self.debug_info += "failed "
        if self.L - self.K > 0:
            self.model.log.debug(f"some error: L={self.L},K={self.K} bankrupted {self}")
        self.model.bank_sector.add_bad_debt(self.K - self.L)
        self.failures += 1
        self.__init__()

    def adjust_capital(self):
        if self.K != (self.A + self.L):
            self.debug_info += f"∆K={self.model.log.format(self.A + self.L - self.K)} "
        return self.A + self.L
