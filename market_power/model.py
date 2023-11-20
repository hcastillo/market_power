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
import statistics


class Model:
    firms = []
    t: int = 0  # current value of time, t = 0..Model.config.T
    bank_sector: BankSector
    bankruptcies = []

    test = False  # it's true when we are inside a test
    log: Log = None
    statistics: Statistics = None
    config: Config = None
    export_datafile = None
    export_description = None

    def __init__(self, firm_class=Firm, **configuration):
        self.config = Config()
        self.log = Log(self)
        self.firm_class = firm_class
        self.statistics = Statistics(self)
        if configuration:
            self.configure(**configuration)

    def configure(self, export_datafile=None, export_description=None, **configuration):
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
                match attribute:
                    case "N":
                        if self.config.N == 0:
                            raise ValueError("For config N values > 0")
                    case "T":
                        if self.config.T == 0:
                            raise ValueError("For config T values > 0")

                    case _:
                        pass
            else:
                raise LookupError(f"attribute '{attribute}' in config not found")
        self.initialize_model(export_datafile=export_datafile, export_description=export_description)

    def initialize_model(self, seed=None,
                         export_datafile=None, export_description=None):

        # what to plot and represent, and in which order
        self.statistics.add(what=Firm, name="K", prepend=" firms   ")
        self.statistics.add(what=Firm, name="A", prepend=" |")
        self.statistics.add(what=Firm, name="L")
        self.statistics.add(what=Firm, name="Y")

        self.statistics.add(what=Firm, name="profits", symbol="π", attr_name="pi")
        self.statistics.add(what=Firm, name="r", function=statistics.mean, repr_function="x̄")
        self.statistics.add(what=Firm, name="Failures", symbol="fail", prepend=" ", attr_name="is_bankrupted",
                            number_type=int)

        self.statistics.add(what=BankSector, name="L", prepend="\n             banks    ")
        self.statistics.add(what=BankSector, name="A", prepend=" | ")
        self.statistics.add(what=BankSector, name="D", prepend=" ")

        self.statistics.add(what=BankSector, name="profits", symbol="π", prepend=" ", plot=False, attr_name="profits")
        self.statistics.add(what=BankSector, name="bad debt",
                            symbol="bd", prepend="", plot=False, attr_name="bad_debt")
        self.statistics.add(what=BankSector, name="credit supply", symbol="cs", prepend="", plot=False,
                            attr_name="credit_supply")

        self.config.__init__()
        random.seed(seed if seed else self.config.default_seed)
        if export_datafile:
            self.export_datafile = export_datafile
        self.export_description = str(self.config) if export_description is None else export_description
        self.firms = []
        for i in range(self.config.N):
            self.firms.append(self.firm_class(new_id=i, its_model=self))
        self.bank_sector = BankSector(self)
        self.statistics.initialize_model(export_datafile=self.export_datafile,
                                         export_description=self.export_description)
        self.log.initialize_model()

    def do_step(self):
        self.bank_sector.bad_debt = 0.0
        self.bank_sector.determine_new_credit_suppy()
        for firm in self.firms:
            firm.do_step()
        self.bank_sector.determine_step_results()
        self.statistics.debug_firms()
        self.log.step(self.statistics.current_status_save())
        self.remove_failed_firms()

    def finish_model(self):
        self.log.finish_model()
        self.statistics.finish_model(export_datafile=self.export_datafile, export_description=self.export_description)

    def run(self, export_datafile=None, values_i_want=None):
        self.initialize_model(export_datafile=export_datafile)
        for self.t in range(self.config.T):
            self.do_step()
        self.finish_model()
        return self.statistics.data

    def remove_failed_firms(self):
        for firm in self.firms:
            if firm.is_bankrupted():
                firm.set_failed()
        self.bank_sector.estimate_total_A_K()
