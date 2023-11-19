#!/usr/bin/env python
# coding: utf-8
"""
ABM model auxiliary file: logging facilities
@author: hector@bith.net
"""
import numpy as np
import math


class StatsArray:
    def __init__(self, its_model, data_type, description,
                 short_description, prepend="", plot=True, attr_name=None, log=False):
        self.description = description
        self.short_description = short_description
        self.model = its_model
        self.prepend = prepend
        self.its_name = ""
        self.log = log
        if attr_name:
            self.attr_name = attr_name
        else:
            self.attr_name = self.short_description
        self.data = np.zeros(its_model.config.T, dtype=data_type)
        self.do_plot = plot

    def get_value(self, element):
        if callable(element):
            return element()
        else:
            return element

    def __return_value_formatted__(self):
        result = f"{self.short_description}"
        result += "Ξ" if self.log else "="
        result += f"{self.model.log.format(self.data[self.model.t])}"
        return result

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
            plt.ylabel(self.description + "(ln)" if self.log else "")
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
    def __init__(self, its_model, data_type, description, short_description,
                 prepend="", plot=True, attr_name=None, function=sum, repr_function="Σ", log=False):
        StatsArray.__init__(self, its_model, data_type, description, short_description, prepend, plot, attr_name, log)
        self.function = function
        self.repr_function = repr_function

    def store_statistics(self):
        result = self.function(self.get_value(getattr(firm, self.attr_name)) for firm in self.model.firms)
        self.data[self.model.t] = math.log(result) if self.log else result
        return self.prepend + self.repr_function + self.__return_value_formatted__()


class StatsBankSector(StatsArray):
    its_name = "Bank"

    def store_statistics(self):
        result = getattr(self.model.bank_sector, self.attr_name)
        self.data[self.model.t] = math.log(result) if self.log else result
        return self.prepend + self.__return_value_formatted__()
