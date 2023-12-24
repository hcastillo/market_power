#!/usr/bin/env python
# coding: utf-8
"""
ABM model

@author: hector@bith.net
"""


class BankSector:
    def __init__(self, its_model, A_i0=None):
        self.model = its_model
        self.bad_debt = 0.0
        self.profits = 0.0
        self.totalA = 0.0
        self.totalK = 0.0
        self.mean_firmK = self.model.config.firms_K_i0
        self.mean_firmA = self.model.config.firms_A_i0
        self.bank_failures = 0
        self.A = A_i0 if A_i0 else self.model.config.bank_sector_A_i0
        self.L = self.determine_new_credit_suppy()
        self.D = self.determine_deposits()
        if self.D < 0:
            raise ValueError("error bank.D<0 due to " +
                             f"D=L-A={self.model.log.format(self.L)}-{self.model.log.format(self.A)}")
        self.estimate_total_a_k()

    def determine_deposits(self):
        # L = A + D, ----> D = L-A
        return self.L - self.A


    def determine_profits(self):
        # (Equation 34)
        profits_loans = 0.0
        total_loans_of_firms = 0.0
        for firm in self.model.firms:
            if not firm.failed:
                profits_loans += firm.r * firm.L
                total_loans_of_firms += firm.L
        remunerations_of_deposits_and_networth = self.determine_average_interest_rate() * total_loans_of_firms
        result = profits_loans - remunerations_of_deposits_and_networth
        self.model.log.debug(f"bank_sector profits={result} = profits_loans({profits_loans}) " +
                             f"- remuneration_deposits_and_assets({remunerations_of_deposits_and_networth})")
        return result

    # def determine_profits(self):
    #     # (Equation 34)
    #     profits_loans = 0.0
    #     total_loans_of_firms = 0.0
    #     for firm in self.model.firms:
    #         if not firm.failed:
    #             profits_loans += firm.r * firm.L
    #             total_loans_of_firms += firm.L
    #     remunerations_of_deposits_and_networth = self.determine_average_interest_rate() * (self.A+self.D)/2
    #     if self.A + profits_loans - remunerations_of_deposits_and_networth - self.bad_debt < 0:
    #         remunerations_of_deposits_and_networth = 0
    #         profits_loans = 0
    #     result = profits_loans - remunerations_of_deposits_and_networth
    #     self.model.log.debug(f"bank_sector profits={result} = profits_loans({profits_loans}) " +
    #                          f"- remuneration_deposits_and_assets({remunerations_of_deposits_and_networth})")
    #     return result

    def determine_average_interest_rate(self):
        if self.model.config.rate_for_bank_deposits_and_networth:
            return self.model.config.rate_for_bank_deposits_and_networth
        else:
            avg_r = sum(firm.r for firm in self.model.firms) / len(self.model.firms)
            return avg_r if avg_r > self.model.config.r_i0 else self.model.config.r_i0

    def determine_net_worth(self):
        # (Equation 35) At = At-1 + profits - bad_debt
        net_worth = self.A + self.profits - self.bad_debt
        self.model.log.debug(f"bank_sector A={net_worth}={self.A}+{self.profits}-{self.bad_debt}")
        if net_worth <= 0:
            # raise Exception(f"bank_sector failed at t={self.model.t+1} A=A + profits - bad_debt " +
            #                 f"--> {net_worth}={self.A}+{self.profits}-{self.bad_debt}")
            self.model.log.error_minor(f"bank_sector failed with A={net_worth}")
            self.bank_failures += 1
            if self.model.config.bank_max_failures_allowed <= self.bank_failures:
                self.model.log.warning(f"bank_sector A={net_worth} -> aborting")
                self.model.abort_execution = True
            else:
                self.model.log.warning(f"A=A_i0 ({net_worth} -> {self.model.config.bank_sector_A_i0})")
                net_worth = self.model.config.bank_sector_A_i0
        return net_worth

    def __str__(self):
        return f"bankSector L={self.model.log.format(self.L)} A={self.model.log.format(self.A)} " + \
            f"D={self.model.log.format(self.D)}"

    def determine_step_results(self):
        self.profits = self.determine_profits()
        self.A = self.determine_net_worth()
        self.L = self.determine_new_credit_suppy()
        self.D = self.determine_deposits()

    def initialize_step(self):
        self.bad_debt = 0
        self.estimate_total_a_k()

    def determine_firm_capacity_loan(self, firm):
        # (Equation 11 of paper a new approach to business fluctuations)
        offeredL = (self.model.config.lambda_param * self.L * firm.K / self.totalK +
                    (1 - self.model.config.lambda_param) * self.L * firm.A / self.totalA)
        self.model.log.debug(f"{firm} bank_sector offeredL={offeredL}")
        return offeredL

    def determine_new_credit_suppy(self):
        credit_supply = self.A / self.model.config.alpha
        self.model.log.debug(f"bank_sector L={credit_supply}")
        return credit_supply

    def add_bad_debt(self, firm):
        amount = firm.L - firm.K
        if amount > 0:
            self.model.log.debug(f"{firm} fails and bank_sector.bad_debt increases in {amount}")
            self.bad_debt += amount
            self.L -= amount
        else:
            self.model.log.debug(f"{firm} fails but no bad_debt")

    def return_loan_from_firm(self, amount_of_loan_to_return, firm_that_returns):
        amount_with_interests = amount_of_loan_to_return + firm_that_returns.r * amount_of_loan_to_return
        self.A += amount_with_interests
        self.L -= amount_of_loan_to_return
        self.model.log.debug(f"{firm_that_returns} returns loan: L-={amount_of_loan_to_return}"+
                             f",A+={amount_with_interests}")

    def estimate_total_a_k(self, info=True):
        total_firms_not_failed = 0
        self.totalA = 0
        self.totalK = 0
        for firm in self.model.firms:
            if not firm.failed:
                self.totalA += firm.A
                self.totalK += firm.K
                total_firms_not_failed += 1
        self.mean_firmK = self.totalK / total_firms_not_failed
        self.mean_firmA = self.totalA / total_firms_not_failed
        if info:
            self.model.log.debug(f"bank_sector Σfirms={total_firms_not_failed} "+
                                 f"firm.A={self.totalA} Σ firm.K={self.totalK}")
