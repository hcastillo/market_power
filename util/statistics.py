#!/usr/bin/env python
# coding: utf-8
"""
ABM model auxiliary file: to have statistics and plot
@author:  hector@bith.net
"""
import numpy as np
from util.log import Log
from util.statsarray import StatsArray

class Statistics:
    OUTPUT_DIRECTORY = "output"

    # This time the idea is to use pandas to store the statistics
    def __init__(self, its_model):
        self.model = its_model
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
        result = " firms   "+self.firmsK.store_statistics_firms("K")

        result += " |"+self.firmsA.store_statistics_firms("A")

        result += self.firmsL.store_statistics_firms("L")

        result += ","+self.firmsY.store_statistics_firms("Y")

        result += self.profits.store_statistics_firms("pi")

        result += " "+self.firmsY.store_statistics_firms("is_bankrupted")

        result += "\n             banks    "+self.bankD.store_statistics_bank("D")

        result += "   "+self.bankA.store_statistics_bank("A")

        result += "|"+self.bankL.store_statistics_bank("L")

        result += " "+self.bad_debt.store_statistics_bank("bad_debt")

        result += " "+self.bank_profits.store_statistics_bank("profits")

        result += " "+self.credit_supply.store_statistics_bank("credit_supply")

        return result

    def reset(self):

        self.failures = StatsArray(self.model,int,"Failures","fail")
        self.firmsK = StatsArray(self.model,float,"Firms K","K")
        self.firmsL = StatsArray(self.model,float,"Firms L","L")
        self.firmsY = StatsArray(self.model,float,"Firms Y","Y")
        self.firmsA = StatsArray(self.model,float,"Firms A","A")
        self.profits = StatsArray(self.model,float,"Firms profits","π")
        self.bankA = StatsArray(self.model,float,"BankSector A","A")
        self.bankL = StatsArray(self.model,float,"BankSector L","L")
        self.bankD = StatsArray(self.model,float,"BankSector A","D")
        self.bank_profits = StatsArray(self.model,float,"BankSector profits","π")
        self.bad_debt = StatsArray(self.model,float,"BankSector bad debt","bd")
        self.credit_supply = StatsArray(self.model,float,"BankSector credit supply","cs")

    def export_data(self, export_datafile=None, export_description=None):
        if export_datafile:
            self.save_data(export_datafile, export_description)

    @staticmethod
    def get_export_path(filename):
        if not filename.startswith(Statistics.OUTPUT_DIRECTORY):
            filename = f"{Statistics.OUTPUT_DIRECTORY}/{filename}"
        return filename if filename.endswith('.txt') else f"{filename}.txt"

    def save_data(self, export_datafile=None, export_description=None):
        if export_datafile:
            with open(Statistics.get_export_path(export_datafile), 'w', encoding="utf-8") as savefile:
                savefile.write('# t\tpolicy\tfitness           \tC                    \tir         \t' +
                               'bankrupts\tbestLenderID\tbestLenderClients\tcreditChannels\n')
                if export_description:
                    savefile.write(f"# {export_description}\n")
                else:

                    savefile.write(f"# {__name__} T={self.model.config.T} N={self.model.config.N}\n")
                for i in range(self.model.config.T):
                    savefile.write(f"{i:3}\t{self.policy[i]:3}\t{self.fitness[i]:19}\t{self.liquidity[i]:19}" +
                                   f"\t{self.interest_rate[i]:20}\t{self.failures[i]:3}" +
                                   f"\t{self.best_lender[i] / self.model.config.N:20}" +
                                   f"\t{self.best_lender_clients[i] / self.model.config.N:20}" +
                                   f"\t{self.credit_channels[i]:3}" +
                                   f"\t{self.rationing[i]:20}" +
                                   f"\t{self.leverage[i]:20}" +
                                   "\n")

    def plot(self):
        pass  # TODO
