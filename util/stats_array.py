#!/usr/bin/env python
# coding: utf-8
"""
ABM model auxiliary file: logging facilities
@author: hector@bith.net
"""
import numpy as np
import types

class StatsArray:
    def __init__(self, its_model, dtype, description,
                 short_description, prepend="", plot=False, property=None):
        self.description = description
        self.short_description = short_description
        self.model = its_model
        self.prepend = prepend
        if property:
            self.property = property
        else:
            self.property = self.short_description
        self.data = np.zeros(its_model.config.T, dtype=dtype)
        self.do_plot = plot

    def __get_value__(self, element):
        if callable(element):
            return element()
        else:
            return element

    def __return_value_formatted__(self):
        return f"{self.short_description}={self.model.log.format(self.data[self.model.t])}"

    def __getitem__(self, t):
        return self.model.log.format(self.data[t])

    def __get__(self):
        return self.data

    def plot(self, show=False):
        if self.do_plot:
            import matplotlib.pyplot as plt
            plt.clf()
            xx = []
            yy = []
            for i in range(self.model.config.T):
                xx.append(i)
                yy.append(self.data[i])
            plt.plot(xx, yy, 'b-')
            plt.ylabel(self.description)
            plt.xlabel("t")
            plt.title(self.description)
            plt.show() if show else plt.savefig(
                self.model.statistics.OUTPUT_DIRECTORY + "/" + self.description.lower().replace(" ", "_") + ".svg")

    def __str__(self):
        if self.its_name != "":
            return self.its_name + "." + self.short_description.upper()
        else:
            return self.short_description.upper()


class StatsFirms(StatsArray):
    its_name= ""

    def store_statistics(self):
        self.data[self.model.t] = sum(self.__get_value__(getattr(firm, self.property)) for firm in self.model.firms)
        return self.prepend +"∑"+self.__return_value_formatted__()


class StatsBankSector(StatsArray):
    its_name = "Bank"

    def store_statistics(self):
        self.data[self.model.t] = getattr(self.model.bank_sector, self.property)
        return self.prepend + self.__return_value_formatted__()

