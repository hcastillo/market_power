#!/usr/bin/env python
# coding: utf-8
"""
ABM model calibrator, using the model
@author: hector@bith.net
"""
import random
from market_power.model import Model
import numpy as np
from progress.bar import Bar
import matplotlib.pyplot as plt

class Experiment1:
    N = 100
    T = 1000
    MC = 10
    analyze_data = ['firms_Y', 'firms_r']
    output = "experiment1/"
    parameters = {
        # [step, min, max]
        # or
        # [ list_of_values_if_greater_than_3 ]
        'eta': [0.0001]
    }

    @staticmethod
    def run_model(model: Model, description, values):
        params = {}
        for i, j in values:
            params[i] = j
        params["T"] = Experiment1.T
        params["N"] = Experiment1.N
        model.statistics.interactive = False
        model.configure(**params)
        data, _ = model.run(export_datafile=description)
        data_considered = {}
        for value in Experiment1.analyze_data:
            if value in data.keys():
                new_data = model.statistics.data[value].data
                data_considered[value] = new_data[~np.isnan(new_data)]
        return data_considered

    @staticmethod
    def next(values=None):
        if len(next(iter(Experiment1.parameters.values()))) > 3:
            return Experiment1.next_list(values)
        else:
            if not values:
                values = []
                for i in Experiment1.parameters:
                    values.append([i, Experiment1.parameters[i][1]])
                return values
            else:
                i = 0
                while i < len(values):
                    if values[i][1] >= Experiment1.parameters[values[i][0]][2]:
                        values[i][1] = Experiment1.parameters[values[i][0]][1]
                        i = i + 1
                    else:
                        values[i][1] += Experiment1.parameters[values[i][0]][0]
                        return values
                return []

    @staticmethod
    def next_list(values):
        if not values:
            values = []
            for i in Experiment1.parameters:
                values.append([i, Experiment1.parameters[i][0]])
            return values
        else:
            i = 0
            while i < len(values):
                j = 0
                while j < len(Experiment1.parameters[values[i][0]]) - 1:
                    if values[i][1] == Experiment1.parameters[values[i][0]][j]:
                        values[i][1] = Experiment1.parameters[values[i][0]][j + 1]
                        for ii in range(i):
                            values[ii][1] = Experiment1.parameters[values[ii][0]][0]
                        return values
                    j = j + 1
                i = i + 1
            return []

    @staticmethod
    def num_models():
        values = Experiment1.next()
        i = 0
        while values:
            i += 1
            values = Experiment1.next(values)
        return i

    @staticmethod
    def empty_array_for_results(is_numpy=True):
        result = {}
        for i_analyze_data in Experiment1.analyze_data:
            result[i_analyze_data] = np.array([]) if is_numpy else []
        return result

    @staticmethod
    def plot(array_with_data, array_with_x_values, filename):
        for i in array_with_data:
            y = []
            e = []
            for j in array_with_data[i]:
                # mean is 0, std is 1:
                y.append(j[0])
                e.append(j[1])
            plt.errorbar(array_with_x_values, y, e, linestyle='None', marker='^')
            plt.savefig(f"{filename}_{i}.png", dpi=300)

    @staticmethod
    def do(model: Model):
        log_experiment = open(f'{Experiment1.output}experiment1.txt', 'w')
        num_models_analyzed = 0
        model.test = False
        values = Experiment1.next()
        progress_bar = Bar('Executing models', max=Experiment1.num_models())
        print(f"# model <id> <parameters> <results, {Experiment1.analyze_data}>", file=log_experiment)
        results_to_plot = Experiment1.empty_array_for_results(is_numpy=False)
        results_x_axis = []
        while values:
            result_iteration = Experiment1.empty_array_for_results()
            for i in range(Experiment1.MC):
                mc_iteration = ["default_seed", random.randint(9999, 20000)]
                values.append(mc_iteration)
                result_mc = Experiment1.run_model(model,
                                                  f"{Experiment1.output}experiment1_{num_models_analyzed}_{i}.csv",
                                                  values)
                values.remove(mc_iteration)
                for i in result_mc.keys():
                    result_iteration[i] = np.concatenate((result_iteration[i], result_mc[i]))
            # time to estimate avg y std of the arrays:
            result_iteration_values = ""
            for i in result_iteration.keys():
                mean_estimated = np.mean(result_iteration[i])
                std_estimated = np.std(result_iteration[i])
                results_to_plot[i].append([mean_estimated, std_estimated])
                result_iteration_values += f" {i}[avg:{mean_estimated},std:{std_estimated}]"
            if len(values) == 1:
                results_x_axis.append(values[0][1])
            else:
                results_x_axis.append(str(values))
            print(f"model #{num_models_analyzed}: {values}: {result_iteration_values}", file=log_experiment)
            values = Experiment1.next(values)
            num_models_analyzed += 1
            progress_bar.next()
        Experiment1.plot(results_to_plot, results_x_axis, f"{Experiment1.output}experiment1")
        log_experiment.close()
        progress_bar.finish()


if __name__ == "__main__":
    Experiment1.do(Model(export_datafile="exec", test=True))
