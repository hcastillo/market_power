#!/usr/bin/env python
# coding: utf-8
"""
ABM model calibrator, using the model
@author: hector@bith.net
"""
from market_power.model import Model


class Callibration:
    N = 100
    T = 2000
    ignore_t_less_than = 600
    analyze_data = ['firmY']

    callibrate = {
        # value : [stepping, min,max]
        'w': [0.01, 0.90, 1.1],
        'k': [0.01, 1.05, 1.30],
        # 'alpha': [0.01, 0.07, 0.09],
    }

    @staticmethod
    def constraints(results, model, description, log_calibration):
        total_bad_debt = sum(i for i in results['bankbad debt'].data[Callibration.ignore_t_less_than:])
        if total_bad_debt > 1e6:
            print(f"error: {description} bank_bad_debt > 1e6", file=log_calibration)
            return False
        i = Callibration.ignore_t_less_than
        for equity in results['bankA'].data[Callibration.ignore_t_less_than:]:
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
        model.configure(params)
        data = model.run(export_datafile=description)
        sum_values = []
        for value in Callibration.analyze_data:
            if value in data.keys():
                sum_values.append(sum(i for i in model.statistics.data[value].data[Callibration.ignore_t_less_than:]))
        if Callibration.constraints(data, model, description, log_calibration):
            return sum_values
        else:
            return []

    @staticmethod
    def next(values=None):
        if not values:
            values = []
            for i in Callibration.callibrate:
                values.append([i, Callibration.callibrate[i][1]])
            return values
        else:
            i = 0
            while i < len(values):
                if values[i][1] >= Callibration.callibrate[values[i][0]][2]:
                    values[i][1] = Callibration.callibrate[values[i][0]][1]
                    i = i + 1
                else:
                    values[i][1] += Callibration.callibrate[values[i][0]][0]
                    return values
            return []

    @staticmethod
    def run(model: Model):
        num_models_analyzed = 0
        log_calibration = open('calibration.txt', 'w')
        values = Callibration.next()
        minimum = 1e10
        best_fit = 0
        best_fit_values = []
        while values:
            print(f"model #{num_models_analyzed}: {values}", file=log_calibration)
            result = Callibration.run_model(model, f"model{num_models_analyzed}.txt", log_calibration, values)
            print(f"model #{num_models_analyzed}: {values}: {result}", log_calibration)
            if result and result[0] < minimum:
                print(f"new best model #{best_fit}", log_calibration)
                best_fit_values = values
            values = Callibration.next(values)
            num_models_analyzed += 1
        print(f"best model is #{best_fit} with {best_fit_values}", log_calibration)
        log_calibration.close()


if __name__ == "__main__":
    # model = Model(export_datafile="exec", bank_sector_A_i0=20, firms_A_i0=2)
    # result = Calibration.run(model,"hola")
    # print(result)
    Callibration.run(Model())
