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
    abort_execution = False

    test = False  # it's true when we are inside a test
    log: Log = None
    statistics: Statistics = None
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
        self.statistics.add(what="bank", name="L", prepend="bank    ")
        self.statistics.add(what="bank", name="A", prepend=" | ")
        self.statistics.add(what="bank", name="D", prepend="  ")
        self.statistics.add(what="bank", name="profits", symbol="π", prepend="  ", attr_name="profits")
        self.statistics.add(what="bank", name="bad debt",
                            symbol="bd", prepend=" ", attr_name="bad_debt")
        self.statistics.add(what="firms", name="K", prepend="\n              firms   ", logarithm=True)
        self.statistics.add(what="firms", name="A", prepend=" |")
        self.statistics.add(what="firms", name="L", prepend=" ", logarithm=True)
        self.statistics.add(what="firms", name="profits", prepend=" ", symbol="π", attr_name="pi")
        self.statistics.add(what="firms", name="Y", prepend=" ", logarithm=True)
        self.statistics.add(what="firms", name="r", prepend=" ", function=statistics.mean)
        self.statistics.add(what="firms", name="I", prepend=" ")
        self.statistics.add(what="firms", name="gamma", prepend=" ", function=statistics.mean, symbol="γ")
        self.statistics.add(what="firms", name="u", function=statistics.mean, repr_function="¯")
        self.statistics.add(what="firms", name="desiredK", symbol="dK", show=False)
        self.statistics.add(what="firms", name="offeredL", symbol="oL", show=False)
        self.statistics.add(what="firms", name="demandL", symbol="dL", show=False)
        self.statistics.add(what="firms", name="failures", attr_name="failed", symbol="fail",
                            number_type=int, prepend=" ")
        # self.statistics.add(what="firm_63", name="L", prepend=" ", show=False)
        # self.statistics.add(what="firm_63", name="K", prepend=" ", show=False)
        # self.statistics.add(what="firm_63", name="A", prepend=" ", show=False)
        # self.statistics.add(what="firm_63", attr_name="is_bankrupted", name="fail", prepend=" ", show=False)
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
        self.bank_sector.initialize_step()
        for firm in self.firms:
            firm.do_step()
        self.bank_sector.determine_step_results()
        step_info = self.statistics.current_status_save()
        self.remove_failed_firms()
        step_info += self.statistics.current_status_save_after_failed_firms_removed()
        self.log.step(step_info)

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
        return self.statistics.data, self.model_title

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
