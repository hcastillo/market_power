#!/usr/bin/env python
# coding: utf-8
"""
ABM model auxiliary file: to have statistics and plot
@author:  hector@bith.net
"""
import numpy as np
from util.log import Log
from util.stats_array import StatsFirms, StatsBankSector


class Statistics:
    OUTPUT_DIRECTORY = "output"

    # This time the idea is to use pandas to store the statistics
    def __init__(self, its_model):
        self.model = its_model
        self.data = {}
        import os
        if not os.path.isdir(self.OUTPUT_DIRECTORY):
            os.mkdir(self.OUTPUT_DIRECTORY)
        self.reset()

    def debug_firms(self, before_start=False):
        for firm in self.model.firms:
            self.debug_firm(firm, before_start=before_start)

    def debug_firm(self, firm, before_start=False):
        text = f"{firm.__str__()} K={Log.format(firm.K)}"
        text += f" | A={Log.format(firm.A)} L={Log.format(firm.L)}"
        if not before_start:
            text += f", Y={Log.format(firm.Y)}"
            text += f" π={Log.format(firm.pi)}"
            text += f" dK={Log.format(firm.desiredK)}"
            text += f" dL/oL={Log.format(firm.desiredL)}/{Log.format(firm.obtainedL)}"
            if firm.is_bankrupted():
                text += "  bankrupted"
        self.model.log.debug(text, before_start)

    def current_status_save(self):
        # it returns also a string with the status
        result = ""
        for item in self.data:
            result += self.data[item].store_statistics()
        return result

    def reset(self):
        self.data["firmsK"] = StatsFirms(self.model, float, "Firms K", "K", prepend=" firms   ")
        self.data["firmsA"] = StatsFirms(self.model, float, "Firms A", "A", prepend=" |")
        self.data["firmsL"] = StatsFirms(self.model, float, "Firms L", "L")
        self.data["firmsY"] = StatsFirms(self.model, float, "Firms Y", "Y", prepend=",")
        self.data["profits"] = StatsFirms(self.model, float, "Firms profits", "π", property="pi")
        self.data["failures"] = StatsFirms(self.model, int, "Failures", "fail", prepend=" ", property="is_bankrupted")
        self.data["bankD"] = StatsBankSector(self.model, float, "BankSector D", "D", prepend="\n             banks    ")
        self.data["bankA"] = StatsBankSector(self.model, float, "BankSector A", "A", prepend="   ", plot=False)
        self.data["bankL"] = StatsBankSector(self.model, float, "BankSector L", "L", prepend="|")
        self.data["bad_debt"] = StatsBankSector(self.model, float, "BankSector bad debt", "bd", prepend=" ",
                                                property="bad_debt")
        self.data["bank_profits"] = StatsBankSector(self.model, float, "BankSector profits", "π", prepend=" ",
                                                    property="profits")
        self.data["credit_supply"] = StatsBankSector(self.model, float, "BankSector credit supply", "cs", prepend=" ",
                                                     property="credit_supply")

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
                    header += "\t"+self.data[item].__str__()
                savefile.write(header+"\n")
                for i in range(self.model.config.T):
                    line = f"{i:3}"
                    for item in self.data:
                        line += "\t" + self.data[item][i]
                    savefile.write(line + "\n")

    def plot(self):
        for item in self.data:
            self.data[item].plot()
