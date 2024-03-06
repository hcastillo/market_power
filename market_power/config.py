#!/usr/bin/env python
# coding: utf-8
"""
ABM model: Configuration parameters

@author: hector@bith.net
"""
import sys


class Config:
    T: int = 1000  # Time (1000)
    N: int = 100   # Number of firms (100)

    eta: float = 0.0001      # ŋ Inverse elasticity: ŋ=1/10000 -> perfect competition, ŋ=1/4 -> high market power

    # firms:                 balance sheet => K = A + L
    firms_K_i0: float = 5.0  # capital
    firms_A_i0: float = 1.0  # assets
    # firms_L_i0: float = 4.0  # loans (from bank sector)  L = k-A
    phi: float = 1.2  # Φ capital productivity: constant in this model without R&D
    threshold_bankrupt = 0  # A < threshold_bankrupt and firm will fail
    g: float = 1.1  # cost per unit of capital
    w: float = 0.5  # real wage
    k: float = 1.0  # capital intensity rate K/N
    b: float = 1  # parameter of bankruptcy cost (b>0)
    beta: float = 0.02  # β skewness parameter -1 ... 1
    # m: float = 0.0  # percentage of K that should be in cash

    # bank sector:                   balance sheet => L = A + D
    bank_sector_A_i0: float = 500  # L and D are set inside bank.py
    r_i0: float = 0.02  # initial rate of interest charged to firms by loans
    lambda_param: float = 0.3  # λ, to determine credit allotted for firms L=A/alfa, 0 < λ < 1
    alpha: float = 0.08  # α ratio equity/loan,  Ls=A/α
    # if you put False or 0, the rate will be the average, as equation 34 says,
    # if it is a number, this fixed value will be used:
    #
    #rate_for_bank_deposits_and_networth: float = 0.04
    rate_for_bank_deposits_and_networth: float = 0
    # if you put 1, it will stop with T=X instead of arriving at the end:
    bank_max_failures_allowed = 1

    # seed used:
    default_seed: int = 20571

    # david parameters

    def __str__(self, separator=""):
        description = sys.argv[0] if not separator else ""
        for attr in dir(self):
            value = getattr(self, attr)
            if isinstance(value, int) or isinstance(value, float):
                description += f" {attr}={value}{separator}"
        return description
