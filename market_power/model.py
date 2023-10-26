#!/usr/bin/env python
# coding: utf-8
"""
ABM model: It contains the firms and the logic to execute the simulation

@author: hector@bith.net
"""
from market_power.bank import BankSector
from market_power.config import Config
from market_power.firm import Firm
from util.log import Log
from util.statistics import Statistics
import random


class Model:
    firms = []
    t: int = 0  # current value of time, t = 0..Model.config.T
    bank_sector: BankSector
    bankruptcies = []

    test = False  # it's true when we are inside a test
    log = None
    statistics = None
    config = None
    export_datafile = None
    export_description = None

    def __init__(self, firm_class=Firm, **configuration):
        self.config = Config()
        self.log = Log(self)
        self.firm_class = firm_class
        self.statistics = Statistics(self)
        if configuration:
            self.configure(**configuration)

    def configure(self, **configuration):
        for attribute in configuration:
            if hasattr(self.config, attribute):
                current_value = getattr(self.config, attribute)
                if isinstance(current_value, int):
                    setattr(self.config, attribute, int(configuration[attribute]))
                else:
                    if isinstance(current_value, float):
                        setattr(self.config, attribute, float(configuration[attribute]))
                    else:
                        raise Exception(f"type of config {attribute} not allowed: {type(current_value)}")
            else:
                raise LookupError("attribute in config not found")
        self.initialize_model()

    def initialize_model(self, seed=None,
                         export_datafile=None, export_description=None):
        self.statistics.reset()
        self.config.__init__()
        random.seed(seed if seed else self.config.default_seed)
        self.export_datafile = export_datafile
        self.export_description = str(self.config) if export_description is None else export_description
        self.firms = []
        for i in range(self.config.N):
            self.firms.append(self.firm_class(new_id=i, its_model=self))
        self.bank_sector = BankSector(self)

    def do_step(self):
        self.bank_sector.cs = self.bank_sector.determine_new_step_credit_suppy()
        for firm in self.firms:
            firm.do_step()
        self.bank_sector.do_step()

        self.log.info(self.statistics.current_status_save())
        self.statistics.debug_firms()
        for firm in self.firms:
            if firm.failed:
                firm.execute_bankruptcy()


    def finish_model(self):
        if not self.test:
            self.statistics.export_data(self.export_datafile, self.export_description)
            self.statistics.plot()
        self.log.info(f" Finish: model T={self.config.T}  N={self.config.N}")

    def run(self, export_datafile=None):
        self.initialize_model(export_datafile=export_datafile)
        for self.t in range(self.config.T):
            self.do_step()
        self.finish_model()
