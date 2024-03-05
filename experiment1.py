#!/usr/bin/env python
# coding: utf-8
"""
ABM model calibrator, using the model
@author: hector@bith.net
"""
import util.utilities as utilities
import statistics
import warnings
from market_power.model import Model
import numpy as np
from progress.bar import Bar
import matplotlib.pyplot as plt
import os


class Experiment1:
    N = 100
    T = 1000
    MC = 10
    analyze_data = ['firms_Y', 'firms_r']
    OUTPUT_DIRECTORY = "experiment1"
    number_of_tries_in_case_of_abort = 3
    parameters = {
        # if instead of a list, you want to use a range, use np.arange(start,stop,step) to generate the list:
        # 'eta': np.arange(0.00001,0.9, 0.1) --> [0.0001, 0.1001, 0.2001... 0.9001]
        #
        'eta': [0.0001, 0.05, 0.1, 0.15, 0.2, 0.3, 0.4]
    }

    @staticmethod
    def manage_stats_options(model):
        model.statistics.add(what="firms", name="Y", prepend=" ", logarithm=True)
        model.statistics.add(what="firms", name="r", prepend=" ", function=statistics.mean)

    @staticmethod
    def run_model(model: Model, description, values):
        values["T"] = Experiment1.T
        values["N"] = Experiment1.N
        model.statistics.interactive = False
        model.configure(**values)
        model.statistics.define_output_directory(Experiment1.OUTPUT_DIRECTORY)
        Experiment1.manage_stats_options(model)
        number_of_tries_in_case_of_abort = Experiment1.number_of_tries_in_case_of_abort
        while number_of_tries_in_case_of_abort > 0:
            data, _ = model.run(export_datafile=description)
            if len(data) == Experiment1.T:
                # when exactly T iterations of data are returned = OK
                number_of_tries_in_case_of_abort -= 1
            else:
                # in case of aborted, we change the seed and run it again:
                model.t = 0
                model.config.default_seed += 1
                model.abort_execution = False
                model.config.T = Experiment1.T
        data_considered = {}
        for value in Experiment1.analyze_data:
            if value in data.keys():
                data_considered[value] = model.statistics.dataframe[value]
        return data_considered

    @staticmethod
    def empty_array_for_results(is_numpy=True):
        result = {}
        for i_analyze_data in Experiment1.analyze_data:
            result[i_analyze_data] = np.array([]) if is_numpy else []
        return result

    @staticmethod
    def plot(array_with_data, array_with_x_values, filename):
        for i in array_with_data:
            use_logarithm = abs(array_with_data[i][0][0]-array_with_data[i][1][0]) > 1e10
            mean = []
            standard_deviation = []
            for j in array_with_data[i]:
                # mean is 0, std is 1:
                mean.append(np.log(j[0]) if use_logarithm else j[0])
                standard_deviation.append(np.log(j[1]/2) if use_logarithm else j[1]/2)
            plt.clf()
            plt.title(f"log({i})" if use_logarithm else f"{i}")
            plt.errorbar(array_with_x_values, mean, standard_deviation, linestyle='None', marker='^')
            plt.savefig(f"{filename}_{i}.png", dpi=300)

    @staticmethod
    def get_num_models():
        return len(list(Experiment1.get_models()))

    @staticmethod
    def get_models():
        return utilities.cartesian_product(Experiment1.parameters)

    @staticmethod
    def do(model: Model):
        if not os.path.isdir(Experiment1.OUTPUT_DIRECTORY):
            os.mkdir(Experiment1.OUTPUT_DIRECTORY)
        log_experiment = open(f'{Experiment1.OUTPUT_DIRECTORY}/experiment1.txt', 'w')
        num_models_analyzed = 0
        model.test = False
        progress_bar = Bar('Executing models', max=Experiment1.get_num_models())
        progress_bar.update()
        results_to_plot = Experiment1.empty_array_for_results(is_numpy=False)
        results_x_axis = []
        for values in Experiment1.get_models():
            result_iteration = Experiment1.empty_array_for_results()
            for i in range(Experiment1.MC):
                mc_iteration = 16141 # random.randint(9999, 20000)
                values['default_seed'] = mc_iteration
                result_mc = Experiment1.run_model(model,
                                                  f"{Experiment1.OUTPUT_DIRECTORY}/experiment1_{num_models_analyzed}_{i}",
                                                  values)
                for j in result_mc.keys():
                    result_iteration[j] = np.concatenate((result_iteration[j], result_mc[j]))
            # time to estimate avg y std of the arrays:
            result_iteration_values = ""
            for k in result_iteration.keys():
                mean_estimated = np.mean(result_iteration[k])
                warnings.filterwarnings('ignore')  # it generates RuntimeWarning: overflow encountered in multiply
                std_estimated = np.std(result_iteration[k])
                results_to_plot[k].append([mean_estimated, std_estimated])
                result_iteration_values += f" {k}[avg:{mean_estimated},std:{std_estimated}]"
            del values['default_seed']
            del values['T']
            del values['N']
            if len(values) == 1:
                results_x_axis.append(list(values.values())[0])
            else:
                results_x_axis.append(str(values))
            print(f"model #{num_models_analyzed}: {values}: {result_iteration_values}", file=log_experiment)
            num_models_analyzed += 1
            progress_bar.next()
        Experiment1.plot(results_to_plot, results_x_axis, f"{Experiment1.OUTPUT_DIRECTORY}/experiment1")
        log_experiment.close()
        progress_bar.finish()


if __name__ == "__main__":
    Experiment1.do(Model(export_datafile="exec", test=True))
