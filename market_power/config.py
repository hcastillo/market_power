#!/usr/bin/env python
# coding: utf-8
"""
ABM model

@author: hector@bith.net
"""
import sys

class Config:
    """
        Configuration parameters for the ABM
        """
    T: int = 1000  # time (1000)
    N: int = 100  # number of firms (100)
    eta: float = 0.25  # ŋ inverse elasticity: ŋ=1/10000 -> perfect competition, ŋ=1/4     -> high market power
    sigma = 0.0  # σ : parameter for the R&D
    sigma_values = []  # list of σ : parameters for the R&D
    alfa: float = 0.08  # α : Basilea's parameter
    mark_up_bank = 0.25  # μ : the mark-up of the bank (μ = 0.0001 for PC; μ = 0.25 for Monopolistic Competition)

    g: float = 1.1
    w: float = 0.005
    k: float = 1

    delta: float = 2  # δ
    b: float = 1
    beta: float = 0.02  # β
    m: float = 0.03
    c: float = 1  # bankruptcy costs' equation
    xi: float = 0.003  # ξ : increase in the productivity of the firms
    rho: float = 0.3  # ρ : parameter for the determination of Bank's expected profits
    share_k: float = 0.5  # this is a parameter that helps to maintain the capital upper a certain threshold
    teta : float = 1 # θ : parameter for the profits of the bank
    fire_sale : float = 1.0 # parameter in order to take into account when selling the firm's own capital in order to repay debts

    # firms and bankSector parameters:
    firms_K_i0: float = 5
    firms_A_i0: float = 1
    firms_L_i0: float = 4
    phi: float = 1.1  # Φ -> this parameter is estimated #todo
    r: float = 0.02  # initial rate of interest charged to firms
    bank_sector_profits : float = 0.0
    bank_sector_B_i0 : float = 0.0

    # there are two models in this code, using False will be without green firms:
    model_green = False

    # seed used:
    default_seed = 20579

    def __init__(self):
        # parameters that come from another values:
        self.gamma: float = ((self.w / self.k) + (self.g * self.r))  # γ : operating cost per unit of capital
        self.bank_sector_L_i0 = self.firms_L_i0 * self.N
        self.bank_sector_A_i0 = (self.N * self.firms_L_i0 * self.alfa)
        self.bank_sector_D_i0 = self.bank_sector_L_i0 - self.bank_sector_A_i0

    def __str__(self):
        description = sys.argv[0]
        for attr in dir(self):
            value = getattr(self, attr)
            if isinstance(value, int) or isinstance(value, float):
                description += f" {attr}={value}"
        return description
