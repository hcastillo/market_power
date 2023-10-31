#!/usr/bin/env python
# coding: utf-8
"""
ABM model: Configuration parameters

@author: hector@bith.net
"""
import sys


class Config:
    T: int = 1000         # Time (1000)
    N: int = 100          # Number of firms (100)
    eta: float = 0.00001  # ŋ Inverse elasticity: ŋ=1/10000 -> perfect competition, ŋ=1/4 -> high market power
    alfa: float = 0.08    # α Basilea's parameter (ratio equity/loan)

    g: float = 1.1        # cost per unit of capital
    w: float = 0.005      # markdown interest rate (the higher it is, the monopolistic power of bank sector)
    k: float = 1.0        # capital intensity rate K/N

    delta: float = 2.0    # δ
    b: float = 1.0        # parameter of bankruptcy cost (b>0)
    beta: float = 0.02    # β skewness parameter -1 ... 1
    m: float = 0.03       # percentage of K that should be in cash

    # firms:
    # balance sheet => K = A + L
    firms_K_i0: float = 5.0  # capital
    firms_A_i0: float = 1.0  # assets
    firms_L_i0: float = 4.0  # loans (from bank sector)
    phi: float = 1.1         # Φ capital productivity: constant in this model without R&D

    # bank sector:
    # balance sheet => L = A + D
    bank_sector_A_i0: float = 32.0  # net worth or assets
    r_i0: float = 0.02              # initial rate of interest charged to firms by loans

    # seed used:
    default_seed: int = 20579

    def __init__(self):
        # parameters that come from another values:
        self.gamma: float = ((self.w / self.k) + (self.g * self.r_i0))  # γ : operating cost per unit of capital
        self.bank_sector_L_i0 = self.firms_L_i0 * self.N
        # self.bank_sector_D_i0 = self.bank_sector_L_i0 - self.bank_sector_A_i0

    def __str__(self):
        description = sys.argv[0]
        for attr in dir(self):
            value = getattr(self, attr)
            if isinstance(value, int) or isinstance(value, float):
                description += f" {attr}={value}"
        return description
