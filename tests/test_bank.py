#!/usr/bin/env python
# coding: utf-8
"""
ABM model tests to verify the functions inside bank.py
@author: hector@bith.net
"""
import pytest
from market_power.model import Model


class TestFirm:
    @pytest.fixture
    def setup(self):
        model = Model()
        model.test = True
        model.configure(N=2, T=2, w=0.005, alpha=0.08, eta=0.000001, phi=1.1, beta=0.02, g=1.1, k=1, b=1)
        model.firms[0].r = 0.03
        model.firms[1].r = 0.05
        yield model

    def test_bank(self, setup):
        avg_r = setup.bank_sector.determine_average_interest_rate()
        assert avg_r == 0.04

