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
            self.debug_info = ""
        self.K = self.model.config.firms_K_i0
        self.A = self.model.config.firms_A_i0
        self.L = self.model.config.firms_L_i0
        self.r = self.model.config.r_i0
        self.gamma = (self.model.config.w / self.model.config.k) + (self.model.config.g * self.r)
        self.phi = self.model.config.phi
        self.pi = self.c = self.Y = self.u = self.gap_of_L = 0.0
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
        self.debug_info += f"γ={self.model.log.format(self.gamma)} " + \
                           f"I={self.model.log.format(self.I)}"
        self.demandL = self.determine_demand_loan()
        self.offeredL = self.model.bank_sector.determine_firm_capacity_loan(self)
        self.L += self.determine_new_loan()
        self.r = self.determine_interest_rate()
        self.c = self.determine_marginal_operating_cost()
        self.debug_info += f"c={self.model.log.format(self.c)} r={self.model.log.format(self.r)} "
        self.Y = self.determine_output()
        self.pi = self.determine_profits()
        self.A = self.determine_net_worth()
        self.K = self.adjust_capital()

    def determine_cost_per_unit_of_capital(self):
        # (Before equation 2)  gamma
        return (self.model.config.w / self.model.config.k) + (self.model.config.g * self.r)

    def determine_marginal_operating_cost(self):
        # (Equation 2)
        return self.gamma / self.phi

    def determine_output(self):
        return self.phi * self.desiredK

    def determine_interest_rate(self):
        # (Equation 33)
        # return random.uniform(0.01, 0.05)   #TODO
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
        return (1 + self.model.config.m) * self.I - self.pi

    def determine_new_loan(self):
        if self.demandL > self.offeredL:
            self.gap_of_L = (self.demandL - self.offeredL)
            self.K -= self.gap_of_L
            self.debug_info += f" gapL={self.model.log.format(self.gap_of_L)} "
            return self.offeredL
        else:
            self.gap_of_L = 0.0
            return self.demandL

    def determine_u(self):
        # stochastic demand [0,2]
        self.u = random.uniform(0, 2)
        self.debug_info += f"u={self.model.log.format(self.u)} "
        return self.u

    def determine_profits(self):
        # (Equation 24)  , but with Y = phi*K
        return self.determine_u() * (self.model.config.eta + (1 - self.model.config.eta) * self.Y) - \
            self.c * self.Y

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
