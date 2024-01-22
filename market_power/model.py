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
from util.stats import Stats
import random

class Model:
    firms = []
    t: int = 0  # current value of time, t = 0..Model.config.T
    bank_sector: BankSector
    bankruptcies = []
    abort_execution = False

    test = False  # it's true when we are inside a test
    log: Log = None
    statistics: Stats = None
    config: Config = None
    export_datafile = None
    export_description = None
    model_id = ""
    model_title = ""

    def __init__(self, firm_class=Firm, test=False, model_id="", log=None, model_title="", **configuration):
        self.config = Config()
        if log:
            self.log = log
            log.model = self
        else:
            self.log = Log(self)
        self.model_id = model_id
        self.model_title = model_title
        self.firm_class = firm_class
        self.test = test
        self.statistics = Stats(self)
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
        self.config.__init__()
        self.abort_execution = False
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
        self.bank_sector.initialize_step()
        for firm in self.firms:
            firm.do_step1()
        self.obtain_sum_a_for_balancing_later()
        for firm in self.firms:
            firm.do_step2()
        self.bank_sector.determine_step_results()
        step_info = self.statistics.current_status_save()
        self.remove_failed_firms()
        step_info += self.statistics.current_status_save_after_failed_firms_removed()
        self.log.step(step_info)

    def obtain_sum_a_for_balancing_later(self):
        self.total_A = 0
        self.negative_A = 0
        self.most_negative_A = 0
        self.most_negative_A_id = None
        for firm in self.firms:
            self.total_A += firm.A
            if firm.A < self.most_negative_A:
                self.most_negative_A = firm.A
                self.most_negative_A_id = firm.id

        # if this company has a negative A higher than the sum of all next companies, it can ruin the model, so we
        # replace it's A by the next one, except of that value is 0
        if abs(self.most_negative_A) > abs(self.total_A-self.most_negative_A):
            next_most_negative = 0
            for firm in self.firms:
                if firm.id != self.most_negative_A_id and firm.A < next_most_negative:
                    next_most_negative = firm.A
            self.firms[self.most_negative_A_id].A = next_most_negative if next_most_negative < 0 else -0.1





    def finish_model(self):
        self.log.finish_model()
        self.statistics.finish_model(export_datafile=self.export_datafile, export_description=self.export_description)

    def run(self, export_datafile=None):
        self.initialize_model(export_datafile=export_datafile)
        for self.t in range(self.config.T):
            self.do_step()
            if self.abort_execution:
                break
        self.finish_model()
        return self.statistics.dataframe, self.model_title

    def remove_failed_firms(self):
        self.bank_sector.estimate_total_a_k(info=False)
        for firm in self.firms:
            if firm.failed:
                # firm.__init__(K=self.bank_sector.mean_firmK,A=self.bank_sector.mean_firmA)
                firm.__init__()

    def get_id(self, short=False):
        if self.model_id:
            return f" model#{self.model_id}" if short else f"model #{self.model_id}"
        else:
            return "" if short else "model"

    def get_id_for_filename(self):
        if self.model_id:
            return f"{self.model_id}_"
        else:
            return ""

    @staticmethod
    def default():
        model_default = Model()
        model_default.test = True
        model_default.model_title = ""
        model_default.model_description = ""
        model_default.log = None
        model_default.t = 0
        model_default.model_id = ""
        return model_default
