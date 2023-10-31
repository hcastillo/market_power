#!/usr/bin/env python
# coding: utf-8
"""
ABM model auxiliary file: logging facilities
@author: hector@bith.net
"""
import numpy as np

class StatsArray:
    def __init__(self, its_model, dtype, description, short_description):
        self.description = description
        self.short_description = short_description
        self.model = its_model
        self.data = np.zeros(its_model.config.T, dtype=dtype)

    def get_statistics_firms(self, property):
        self.data[self.model.t] = sum(getattr(firm, property) for firm in self.model.firms)
        return "∑"+self.__return_value_formatted__()


    def get_statistics_bank(self, property):
        self.data[self.model.t] = getattr(self.model.bank_sector, property)
        return self.__return_value_formatted__()

    def __return_value_formatted__(self):
        return f"{self.short_description} = {self.model.log.format(self.data[self.model.t])}"