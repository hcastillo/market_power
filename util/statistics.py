#!/usr/bin/env python
# coding: utf-8
"""
ABM model auxiliary file: to have statistics and plot
@author:  hector@bith.net
"""
import numpy as np
from util.log import Log


class Statistics:
    OUTPUT_DIRECTORY = "../output"

    # This time the idea is to use pandas to store the statistics
    def __init__(self, its_model):
        self.model = its_model
        import os
        if not os.path.isdir(self.OUTPUT_DIRECTORY):
            os.mkdir(self.OUTPUT_DIRECTORY)
        self.reset()

    def debug_firms(self):
        for firm in self.model.firms:
            self.debug_firm(firm)

    def debug_firm(self, firm):
        text = f"{firm.__str__()} K={Log.__format_number__(firm.K)}"
        text += f" | A={Log.__format_number__(firm.A)} L={Log.__format_number__(firm.L)}"
        text += f",  dK={Log.__format_number__(firm.dK)}"
        text += f"  dL/oL={Log.__format_number__(firm.desiredL)}/{Log.__format_number__(firm.obtainedL)}"
        text += f"  Y={Log.__format_number__(firm.Y)}"
        text += f"  π={Log.__format_number__(firm.pi)}"
        self.model.log.debug(text)

    def current_status_save(self):
        # it returns also a string with the status
        result = ""

        self.firmsK[self.model.t] = sum(float(firm.K) for firm in self.model.firms)
        result += f"firms ∑K={self.firmsK[self.model.t]:10.2f}"

        self.firmsA[self.model.t] = sum(float(firm.A) for firm in self.model.firms)
        result += f" ∑A={self.firmsA[self.model.t]:10.2f}"

        self.firmsL[self.model.t] = sum(float(firm.L) for firm in self.model.firms)
        result += f" ∑L={self.firmsL[self.model.t]:10.2f}"

        self.firmsY[self.model.t] = sum(float(firm.Y) for firm in self.model.firms)
        result += f" ∑Y={self.firmsY[self.model.t]:10.2f}"

        result += f" fails={self.failures[self.model.t]:<2}"

        self.bankA[self.model.t] = self.model.bank_sector.A
        result += f"\n            banks ∑A={self.model.bank_sector.A:10.2f}"

        self.bankD[self.model.t] = self.model.bank_sector.D
        result += f" ∑D={self.model.bank_sector.D:10.2f}"

        self.bankL[self.model.t] = self.model.bank_sector.L
        result += f" ∑L={self.model.bank_sector.L:10.2f}"

        return result

    def reset(self):
        self.failures = np.zeros(self.model.config.T, dtype=int)
        self.firmsK = np.zeros(self.model.config.T, dtype=float)
        self.firmsA = np.zeros(self.model.config.T, dtype=float)
        self.firmsL = np.zeros(self.model.config.T, dtype=float)
        self.firmsY = np.zeros(self.model.config.T, dtype=float)
        self.bankA = np.zeros(self.model.config.T, dtype=float)
        self.bankL = np.zeros(self.model.config.T, dtype=float)
        self.bankD = np.zeros(self.model.config.T, dtype=float)

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
