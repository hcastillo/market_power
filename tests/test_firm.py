#!/usr/bin/env python
# coding: utf-8
"""
ABM model tests to verify the functions inside firm
@author: hector@bith.net
"""
import pytest
from market_power.model import Model


class TestFirm:
    @pytest.fixture
    def model_setup(self):
        model = Model()
        model.test = True
        model.configure(N=2, T=2, w=0.005, alpha=0.08, eta=0.000001, phi=1.1, beta=0.02, g=1.1, k=1, b=1, m=0)
        yield model

    def test_firm_ok(self, model_setup):
        firm = model_setup.firms[0]

        firm.gamma = firm.determine_cost_per_unit_of_capital()
        assert firm.gamma == 0.027000000000000003

        firm.desiredK = firm.determine_desired_capital()
        assert firm.desiredK == 54.646391481518506

        firm.I = firm.determine_investment()
        assert firm.I == 49.646391481518506

        firm.demandL = firm.determine_demand_loan()
        assert firm.demandL == 53.646391481518506

        firm.offeredL = model_setup.bank_sector.determine_firm_capacity_loan(firm)
        assert firm.offeredL == 2500000.0

        firm_previous_K = firm.K
        firm.L += firm.determine_new_loan()
        assert firm.L == 57.646391481518506
        assert firm.gap_of_L == 0
        assert firm_previous_K == firm.K

    def test_firm_failing(self, model_setup):
        firm = model_setup.firms[1]
        firm.gamma = firm.determine_cost_per_unit_of_capital()
        assert firm.gamma == 0.027000000000000003

        firm.desiredK = firm.determine_desired_capital()
        assert firm.desiredK == 54.646391481518506

        firm.I = firm.determine_investment()
        assert firm.I == 49.646391481518506

        firm.demandL = firm.determine_demand_loan()
        assert firm.demandL == 53.646391481518506

        firm.offeredL = 10.0
        firm_previous_K = firm.K
        firm_previous_L = firm.L
        firm.L += firm.determine_new_loan()
        assert firm.L == 10.0 + firm_previous_L
        assert firm.gap_of_L == 43.646391481518506
        assert firm.K == firm_previous_K

