#!/usr/bin/env python
# coding: utf-8
"""
ABM model auxiliary file: to have statistics and plot
@author:  hector@bith.net
"""
from util.log import Log
from util.stats_array import StatsFirms, StatsBankSector
from market_power.bank import BankSector


class Statistics:
    OUTPUT_DIRECTORY = "output"
    enable_plot = False

    # This time the idea is to use pandas to store the statistics
    def __init__(self, its_model):
        self.model = its_model
        self.data = {}
        import os
        if not os.path.isdir(self.OUTPUT_DIRECTORY):
            os.mkdir(self.OUTPUT_DIRECTORY)

    def debug_firms(self, before_start=False):
        for firm in self.model.firms:
            self.debug_firm(firm, before_start=before_start)

    def debug_firm(self, firm, before_start=False):
        text = f"{firm.__str__()} K={Log.format(firm.K)}"
        text += f" | A={Log.format(firm.A)} L={Log.format(firm.L)}"
        if not before_start:
            # text += f", Y={Log.format(firm.Y)}"
            text += f" π={Log.format(firm.pi)}"
            # text += f" γ={Log.format(firm.gamma)}"
            text += f" dK={Log.format(firm.desiredK)}"
            text += f" dL/oL={Log.format(firm.demandL)}/{Log.format(firm.offeredL)}"
            text += " bankrupted" if firm.is_bankrupted() else ""
            text += " " + firm.debug_info
        self.model.log.debug(text, before_start)

    def current_status_save(self):
        # it returns also a string with the status
        result = ""
        for item in self.data:
            result += self.data[item].store_statistics()
        return result

    def add(self, what, name, prepend="", symbol=None, attr_name=None, number_type=float, function=sum,
            plot=True, log=False):
        if not attr_name:
            attr_name = name
        if not symbol:
            symbol = name.replace(" ", "_")
            if len(symbol) != len(name):
                symbol = symbol.lower()
        if not callable(function):
            raise TypeError("function parameter should be a callable type")
        if what == BankSector:
            self.data["bank"+name] = StatsBankSector(self.model, number_type, name, symbol, prepend=prepend, plot=plot,
                                                     attr_name=attr_name, log=log)
        else:
            self.data["firm"+name] = StatsFirms(self.model, number_type, name, symbol, prepend=prepend,
                                                function=function, plot=plot, attr_name=attr_name, log=log)

    @staticmethod
    def get_export_path(filename):
        if not filename.startswith(Statistics.OUTPUT_DIRECTORY):
            filename = f"{Statistics.OUTPUT_DIRECTORY}/{filename}"
        return filename if filename.endswith('.txt') else f"{filename}.txt"

    def export_data(self, export_datafile=None, export_description=None):
        if export_datafile:
            with open(Statistics.get_export_path(export_datafile), 'w', encoding="utf-8") as savefile:
                if export_description:
                    savefile.write(f"# {export_description}\n")
                else:
                    savefile.write(f"# {__name__} T={self.model.config.T} N={self.model.config.N}\n")
                header = "# t"
                for item in self.data:
                    header += "\t" + self.data[item].__str__()
                savefile.write(header + "\n")
                for i in range(self.model.config.T):
                    line = f"{i:3}"
                    for item in self.data:
                        line += "\t" + self.data[item][i]
                    savefile.write(line + "\n")

    def plot(self):
        if self.enable_plot:
            for item in self.data:
                self.data[item].plot()
