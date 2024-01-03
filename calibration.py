#!/usr/bin/env python
# coding: utf-8
"""
ABM model calibrator, using the model
@author: hector@bith.net
"""
from market_power.model import Model
import numpy as np
from progress.bar import Bar


class Calibration:
    N = 100
    T = 1000
    ignore_t_less_than = 400
    analyze_data = ['firms_Y', 'firms_L']
    parameters = {
        # value : [stepping, min,max]
        'eta': [0.1, 0.0001, 0.9],
        # 'k': [0.2, 1.04, 1.10],
        # 'alpha': [0.01, 0.07, 0.09],
    }

    @staticmethod
    def constraints(results, model, description, log_calibration):
        total_bad_debt = sum(i for i in results['bank_bad_debt'].data[Calibration.ignore_t_less_than:])
        if total_bad_debt > 1e16:
            print(f"error: {description} bank_bad_debt > 1e16", file=log_calibration)
            return False
        if model.t < Calibration.T-1:
            print(f"error: {description} steps t={model.t} instead of {Calibration.T}", file=log_calibration)
        i = Calibration.ignore_t_less_than
        for equity in results['bank_A'].data[Calibration.ignore_t_less_than:]:
            if equity < 0:
                print(f"error: {description} bankA<0 in step {i}", file=log_calibration)
                i += 1
                return False
        # if no constraint not Ok, then true
        return True

    @staticmethod
    def run_model(model: Model, description, log_calibration, values):
        params = {}
        for i, j in values:
            params[i] = j
        params["T"] = Calibration.T
        params["N"] = Calibration.N
        model.statistics.interactive = False
        model.configure(**params)
        data, _ = model.run(export_datafile=description)
        data_considered = []
        for value in Calibration.analyze_data:
            if value in data.keys():
                data_considered.append(np.nanmean(model.statistics.data[value].data[Calibration.ignore_t_less_than:]))
        if Calibration.constraints(data, model, description, log_calibration):
            return data_considered
        else:
            return []

    @staticmethod
    def next(values=None):
        if not values:
            values = []
            for i in Calibration.parameters:
                values.append([i, Calibration.parameters[i][1]])
            return values
        else:
            i = 0
            while i < len(values):
                if values[i][1] >= Calibration.parameters[values[i][0]][2]:
                    values[i][1] = Calibration.parameters[values[i][0]][1]
                    i = i + 1
                else:
                    values[i][1] += Calibration.parameters[values[i][0]][0]
                    return values
            return []

    @staticmethod
    def estimate_models():
        values = Calibration.next()
        i = 0
        while values:
            i+=1
            values = Calibration.next(values)
        return i

    @staticmethod
    def calibrate(model: Model):
        num_models_analyzed = 0
        log_calibration = open('calibration.txt', 'w')
        values = Calibration.next()
        minimum = 1e10
        best_fit = 0
        best_fit_values = []
        model.test = False
        progress_bar = Bar('Executing models', max=Calibration.estimate_models())
        print(f"# model <id> <parameters> <results, {Calibration.analyze_data}>", file=log_calibration)
        while values:
            result = Calibration.run_model(model, f"model{num_models_analyzed}.txt", log_calibration, values)
            print(f"model #{num_models_analyzed}: {values}: {result}", file=log_calibration)
            if result and result[0] < minimum:
                # print(f"new best model #{best_fit}", file=log_calibration)
                best_fit_values = values
            values = Calibration.next(values)
            num_models_analyzed += 1
            progress_bar.next()
        print(f"best model is #{best_fit} with {best_fit_values}", file=log_calibration)
        log_calibration.close()
        progress_bar.finish()


if __name__ == "__main__":
    Calibration.calibrate(Model(export_datafile="exec", test=True))
