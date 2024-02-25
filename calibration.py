#!/usr/bin/env python
# coding: utf-8
"""
ABM model calibrator, using the model
@author: hector@bith.net
"""
from market_power.model import Model
import numpy as np
from progress.bar import Bar
import util.utilities as utilities
import statistics
import pandas as pd


class Calibration:
    N = 100
    T = 1000
    ignore_t_less_than = 400
    parameters = {
        # if instead of a list, you want to use a range, use np.arange(start,stop,step) to generate the list:
        # 'eta': np.arange(0.00001,0.9, 0.1) --> [0.0001, 0.1001, 0.2001... 0.9001]
        #
        'eta': np.arange(0.0001, 0.9, 0.1),
        # 'alpha': [0.01, 0.07, 0.09],
    }

    @staticmethod
    def manage_stats_options(model):
        model.statistics.add(what="firms", name="Y", function=statistics.mean)
        model.statistics.add(what="firms", name="L", function=statistics.mean)
        model.statistics.add(what="bank", name="bad debt", symbol="bd", attr_name="bad_debt")
        model.statistics.add(what="bank", name="A")

    @staticmethod
    def constraints(results, model, description, log_calibration):
        total_bad_debt = sum(i for i in results['bank_bad_debt'])
        if total_bad_debt > 1e16:
            print(f"error: {description} bank_bad_debt > 1e16", file=log_calibration)
            return False
        if model.t < Calibration.T-1:
            print(f"error: {description} steps t={model.t} instead of {Calibration.T}", file=log_calibration)
        i = Calibration.ignore_t_less_than
        for equity in results['bank_A']:
            if equity < 0:
                print(f"error: {description} bankA<0 in step {i}", file=log_calibration)
                i += 1
                return False
        # if no constraint not Ok, then true
        return True

    @staticmethod
    def get_num_models():
        return len(list(Calibration.get_models()))

    @staticmethod
    def get_models():
        return utilities.cartesian_product(Calibration.parameters)

    @staticmethod
    def run_model(model: Model, description, log_calibration, values):
        values["T"] = Calibration.T
        values["N"] = Calibration.N
        model.statistics.interactive = False
        model.configure(**values)
        Calibration.manage_stats_options(model)
        data, _ = model.run(export_datafile=description)
        # data.to_csv("test.csv", index=False)
        if Calibration.constraints(data.loc[Calibration.ignore_t_less_than:], model, description, log_calibration):
            return data
        else:
            return pd.DataFrame([])

    @staticmethod
    def calibrate(model: Model):
        current_model_in_analysis = 0
        log_calibration = open('calibration.txt', 'w')
        minimum = 1
        best_fit = 0
        best_fit_values = []
        model.test = False
        progress_bar = Bar('Executing models', max=Calibration.get_num_models())
        print(f"# model <id> <parameters> <results>", file=log_calibration)
        for values in Calibration.get_models():
            result = Calibration.run_model(model, f"model{current_model_in_analysis}.txt", log_calibration, values)
            print(f"model #{current_model_in_analysis}: {values}: Y:{result['firms_Y'].mean()}", file=log_calibration)
            if not result.empty and result['firms_Y'].mean()>minimum:
                best_fit_values = values
                best_fit = current_model_in_analysis
                minimum = result['firms_Y'].mean()
            current_model_in_analysis += 1
            progress_bar.next()
        print(f"best model (greater Y) is #{best_fit} with {best_fit_values}", file=log_calibration)
        log_calibration.close()
        progress_bar.finish()


if __name__ == "__main__":
    Calibration.calibrate(Model(export_datafile="exec", test=True))
