#!/usr/bin/env python
# coding: utf-8
"""
ABM model

@author: hector@bith.net
"""
import random


class Firm:
    def __init__(self, new_id=None, its_model=None, K=None, A=None):
        if its_model:
            self.id = new_id
            self.model = its_model
            self.failures = 0
        self.K = self.model.config.firms_K_i0 if K is None else K
        self.A = self.model.config.firms_A_i0 if A is None else A
        self.L = self.K - self.A  # self.model.config.firms_L_i0
        self.failed = False
        self.r = self.model.config.r_i0
        self.gamma = (self.model.config.w / self.model.config.k) + (self.model.config.g * self.r)
        self.phi = self.model.config.phi
        self.pi = 0.0
        self.c = 0.0
        self.Y = 0.0
        self.u = 0.0
        self.MR = 0.0
        self.MC = 0.0
        self.gap_of_L = 0.0
        self.desiredK = 0.0
        self.demandL = 0.0
        self.offeredL = 0.0
        self.I = 0.0

    def __str__(self, short: bool = False):
        init = "firm#" if not short else "#"
        if self.failures > 0:
            return f"{init}{self.id}.{self.failures:<2}"
        else:
            return f"{init}{self.id}   "

    def do_step1(self):
        self.gamma = self.determine_cost_per_unit_of_capital()
        self.desiredK = self.determine_desired_capital()
        self.I = self.determine_investment()
        self.demandL = self.determine_demand_loan()
        self.offeredL = self.model.bank_sector.determine_firm_capacity_loan(self)
        self.L = self.determine_new_loan()
        self.K = self.adjust_capital()
        self.r = self.determine_interest_rate()
        self.c = self.determine_marginal_operating_cost()
        self.Y = self.determine_output()  # not used in pi, substituted by phi*K
        self.u = self.determine_u()
        self.pi = self.determine_profits()

        self.MC = self.determine_marginal_cost()
        self.MR = self.determine_marginal_revenue()

        self.A = self.determine_net_worth()

    def do_step2(self):
        ###self.A += self.adjust_net_worth()
        self.K = self.adjust_capital()
        self.Y = self.determine_output()  # second time
        if self.is_bankrupted():
            self.set_failed()

    def adjust_net_worth(self):
        if self.A < 0 and self.model.total_A < 0:
            return abs(self.model.total_A)*self.A/self.model.negative_A
        else:
            return 0

    def determine_marginal_cost(self):
        # (Equation 13, right part c*b)
        return self.c + self.model.config.b / 2 * (
            self.c * (2+self.model.config.eta) * self.Y**(1+self.model.config.eta)
            -
            self.A * (1+self.model.config.eta) * self.Y**(self.model.config.eta)
        )

    def determine_marginal_revenue(self):
        # (Equation 13, left part MR)
        return (1-self.model.config.eta)*self.Y**self.model.config.eta

    def determine_cost_per_unit_of_capital(self):
        # (Before equation 2)  gamma
        gamma = (self.model.config.w / self.model.config.k) + (self.model.config.g * self.r)
        self.model.log.debug(f"{self} γ={gamma}")
        return gamma

    def determine_marginal_operating_cost(self):
        # (Equation 2)
        c = self.gamma / self.phi
        self.model.log.debug(f"{self} c={c}")
        return c

    def determine_output(self):
        output = self.phi * self.K
        self.model.log.debug(f"{self} Y={output}")
        return output

    def determine_interest_rate(self):
        # (Equation 33)
        rate = self.model.config.beta * self.L / self.A
        self.model.log.debug(f"{self} r={rate}")
        return rate

    def determine_desired_capital(self):
        # (Equation 22)
        desiredK = (1 - self.model.config.eta) ** 2 / (self.model.config.b * self.gamma) - \
                   (1 - self.model.config.eta) / (self.model.config.b * self.phi) + \
                   self.A / (2 * self.gamma)
        self.model.log.debug(f"{self} desiredK={desiredK}")
        return desiredK

    def determine_investment(self):
        # (Below equation 33)
        investment = self.desiredK - self.K
        self.model.log.debug(f"{self} I={investment}")
        return investment

    def determine_demand_loan(self):
        # (Over equation 33)
        demandL = self.L + self.I - self.pi
        self.model.log.debug(f"{self} demandL={demandL}")
        return demandL

    def determine_new_loan(self):
        if self.demandL > self.offeredL:
            self.gap_of_L = (self.demandL - self.offeredL)
            self.model.log.debug(f"{self} L=oL={self.offeredL} gapL={self.gap_of_L}")
            return self.offeredL
        else:
            self.gap_of_L = 0.0
            if self.demandL < 0:
                return self.reduce_loans_with_bank(self.demandL)
            else:
                self.model.log.debug(f"{self} L=dL={self.demandL}")
                return self.demandL

    def reduce_loans_with_bank(self, negative_demand_of_L):
        self.model.bank_sector.return_loan_from_firm(-negative_demand_of_L, self)
        new_loan = self.L + negative_demand_of_L
        if new_loan < 0:
            self.model.log.debug(f"{self} L=0,dL=0")
            return 0
        else:
            self.model.log.debug(f"{self} L={new_loan},dL=0")
            return new_loan

    def determine_u(self):
        # stochastic demand [0,2]
        u = random.uniform(0, 2)
        self.model.log.debug(f"{self} u={u}")
        return u

    def determine_profits(self):
        # (Equation 24)  , but with Y = phi*K and simplifying
        profits = (self.u * (self.model.config.eta + (1 - self.model.config.eta) * self.model.config.phi * self.K)) - \
                  (self.gamma * self.K)
        # profits = self.u * (self.model.config.eta + ((1 - self.model.config.eta) * self.Y)) - \
        #          ((self.gamma / self.model.config.phi) * self.Y)
        self.model.log.debug(f"{self} π={profits}")
        return profits

    def determine_net_worth(self):
        # (Equation 8)
        new_A = self.A + self.pi
        self.model.log.debug(f"{self} A={new_A}")
        return new_A

    def is_bankrupted(self):
        return self.A < self.model.config.threshold_bankrupt

    def set_failed(self):
        self.model.bank_sector.add_bad_debt(self)
        self.failures += 1
        self.failed = True

    def adjust_capital(self):
        newK = self.A + self.L
        self.model.log.debug(f"{self} K={newK}")
        return newK
