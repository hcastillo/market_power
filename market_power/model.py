#!/usr/bin/env python
# coding: utf-8
"""
ABM model

@author: hector@bith.net
"""
from market_power.bank import BankSector
from market_power.config import Config
from market_power.firm import Firm
from util.log import Log
from util.statistics import Statistics
import random


class Model:
    """
    It contains the firms and the logic to execute the simulation
    """
    firms = []
    t: int = 0  # current value of time, t = 0..Model.config.T
    bank_sector: BankSector
    bankruptcies = []

    test = False  # it's true when we are inside a test
    debug = None  # if not None, we will debug at this instant i, entering in interactive mode
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
            self.firms.append( self.firm_class(new_id=i, its_model=self))
        self.bank_sector = BankSector(self)


    def removeBankruptedFirms(self):     #TODO: please Hector tell me if this method is good or not for removing defaulted firms
        i = 0                       # counter for defaulted firms
        self.bank_sector.B = 0.0
        for firm in self.firms:
            if firm.A < 0:
                bankrupted_id = firm.id
                if firm.L > (self.config.fire_sale * firm.K):
                    self.bank_sector.B += (firm.L - (self.config.fire_sale * firm.K))
                    self.bank_sector.A -= self.bank_sector.B
                    self.bank_sector.D = (self.bank_sector.L - self.bank_sector.A)
                else:
                    self.bank_sector.B += 0
                self.firms.remove(firm)
                i += 1
                new_firm = self.firm_class(new_id = bankrupted_id, its_model = self)    # it creates a new firm with the same ID as you prefer
                self.firms.append(new_firm)
        self.bankruptcies.append(i)     # I created a list to take into account all the bankruptcies that happen during the time
        return i


    def do_step(self):
        self.bank_sector.cs = self.bank_sector.determineCreditSupply()  # firstly, I must determine the credit supply
        # of the bank and later I can perform the operations related to firms
        for firm in self.firms:
            firm.do_step()
            # self.log.info("initialize_step")
            # self.log.debug("hello, this is a debug")
            self.bank_sector.cs -= firm.L  # TODO: we need to introduce a control by which if the bank's credit
                                           # supply finishes, the firms cannot ask for a loan
        self.bank_sector.do_step()
        self.removeBankruptedFirms()        #TODO: Hector do you think this is an appropriate function for removing and adding firms?




    def finish_step(self):
        self.log.info(self.statistics.current_status_save())
        self.statistics.debug_firms()

    def finish_model(self):
        if not self.test:
            self.statistics.export_data(self.export_datafile, self.export_description)
            self.statistics.plot()
        self.log.info(f" Finish: model T={self.config.T}  N={self.config.N}")

    def run(self,export_datafile=None):
        self.initialize_model(export_datafile=export_datafile)
        for self.t in range(self.config.T):
            self.do_step()
            self.finish_step()
        self.finish_model()
