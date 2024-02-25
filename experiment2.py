#!/usr/bin/env python
# coding: utf-8
"""
ABM model calibrator, using the model
@author: hector@bith.net
"""
import random
import numpy as np
import util.utilities as utilities
from util.stats_array import PlotMethods
import statistics
from market_power.model import Model
import warnings
import pandas as pd
from progress.bar import Bar
import matplotlib.pyplot as plt
import os
import math


class Experiment2:
    N = 100
    T = 1000
    MC = 10
    analyze_data = ['firms_Y', 'firms_A', 'bank_A', 'firms_r']
    OUTPUT_DIRECTORY = "experiment2"
    beta = {
        # if instead of a list, you want to use a range, use np.arange(start,stop,step) to generate the list:
        # 'eta': np.arange(0.00001,0.9, 0.1) --> [0.0001, 0.1001, 0.2001... 0.9001]
        #
        'beta': [0.02, 0.03, 0.04, 0.05],
        'g': [1.0, 1.1, 1.2],
        'k': [1.0, 1.1, 1.2],
        'w': [0.5,0.6,0.7]
    }
    eta = {
        'eta': [0.0001, 0.1, 0.25]
    }

    @staticmethod
    def manage_stats_options(model):
        model.statistics.add(what="firms", name="Y", prepend=" ", logarithm=True)
        model.statistics.add(what="firms", name="A", prepend=" ", logarithm=True)
        model.statistics.add(what="firms", name="r", prepend=" ", function=statistics.mean)

    @staticmethod
    def run_model(model: Model, description, values):
        values["T"] = Experiment2.T
        values["N"] = Experiment2.N
        model.statistics.interactive = False
        model.configure(**values)
        model.statistics.define_output_directory(Experiment2.OUTPUT_DIRECTORY)
        Experiment2.manage_stats_options(model)
        if description.endswith("_0"):
            # only the first model is plotted:
            model.statistics.enable_plotting(plot_format=PlotMethods.get_default(),
                                             plot_min=0, plot_max=Experiment2.T, plot_what='firms_Y,firms_failures,bank_bad_debt')
        data, _ = model.run(export_datafile=description)
        return data

    @staticmethod
    def plot(array_with_data, array_with_x_values, title, title_x, filename):
        for i in array_with_data:
            use_logarithm = abs(array_with_data[i][0][0] - array_with_data[i][1][0]) > 1e10
            mean = []
            standard_deviation = []
            for j in array_with_data[i]:
                # mean is 0, std is 1:
                mean.append(np.log(j[0]) if use_logarithm else j[0])
                standard_deviation.append(np.log(j[1] / 2) if use_logarithm else j[1] / 2)
            plt.clf()
            plt.title(title)
            plt.xlabel(title_x)
            plt.title(f"log({i})" if use_logarithm else f"{i}")
            plt.errorbar(array_with_x_values, mean, standard_deviation, linestyle='None', marker='^')
            plt.savefig(f"{filename}_{i}.png", dpi=300)

    @staticmethod
    def plot_ddf(array_with_data, title, filename):
        plt.clf()
        plt.title(title + " ddf")
        plt.xlabel("log firm_a")
        plt.ylabel("log rank")
        xx = []
        yy = []
        sorted = array_with_data['firms_A'].sort_values(ascending=False)
        j = 1
        for i in sorted:
            if not np.isnan(i) and i > 0:
                xx.append(math.log(i))
                yy.append(math.log(j))
                j += 1
        plt.plot(xx, yy,"ro")
        plt.savefig(f"{filename}_ddf.png", dpi=300)

    @staticmethod
    def get_num_models(parameters):
        return len(list(Experiment2.get_models(parameters)))

    @staticmethod
    def get_models(parameters):
        return utilities.cartesian_product(parameters)

    @staticmethod
    def do(model: Model):
        if not os.path.isdir(Experiment2.OUTPUT_DIRECTORY):
            os.mkdir(Experiment2.OUTPUT_DIRECTORY)
        log_experiment = open(f'{Experiment2.OUTPUT_DIRECTORY}/experiment2.txt', 'w')
        num_models_analyzed = 0
        model.test = False

        progress_bar = Bar('Executing models', max=Experiment2.get_num_models(Experiment2.beta) *
                                                   Experiment2.get_num_models(Experiment2.eta))
        progress_bar.update()
        for beta in Experiment2.get_models(Experiment2.beta):
            results_to_plot = {}
            results_x_axis = []
            for eta in Experiment2.get_models(Experiment2.eta):
                values = beta.copy()
                values.update(eta)
                result_iteration = pd.DataFrame()
                aborted_models = 0
                for i in range(Experiment2.MC):
                    mc_iteration = random.randint(9999, 20000)
                    values['default_seed'] = mc_iteration
                    result_mc = Experiment2.run_model(model,
                                                      f"{Experiment2.OUTPUT_DIRECTORY}/experiment2_{num_models_analyzed}_{i}",
                                                      values)
                    if len(result_mc) != Experiment2.T:
                        aborted_models += 1
                    result_iteration = pd.concat([result_iteration, result_mc])
                Experiment2.plot_ddf(result_iteration, f"{beta}{eta}",
                                     f"{Experiment2.OUTPUT_DIRECTORY}/experiment2_{num_models_analyzed}_{i}")
                result_iteration_values = ""
                for k in result_iteration.keys():
                    mean_estimated = result_iteration[k].mean()
                    warnings.filterwarnings('ignore')  # it generates RuntimeWarning: overflow encountered in multiply
                    std_estimated = result_iteration[k].std()
                    if k in results_to_plot:
                        results_to_plot[k].append([mean_estimated, std_estimated])
                    else:
                        results_to_plot[k] = [[mean_estimated, std_estimated]]
                    result_iteration_values += f" {k}[avg:{mean_estimated},std:{std_estimated}]"
                del values['default_seed']
                del values['T']
                del values['N']
                results_x_axis.append(str(eta['eta']) + ("*" if aborted_models else ""))

                if aborted_models:
                    result_iteration_values = (f"aborted_models={aborted_models}/{Experiment2.MC} "
                                               + result_iteration_values)
                print(f"model #{num_models_analyzed}: {values}: {result_iteration_values}", file=log_experiment)
                num_models_analyzed += 1
                progress_bar.next()
            Experiment2.plot(results_to_plot, results_x_axis, beta, "eta",
                             f"{Experiment2.OUTPUT_DIRECTORY}/beta{beta['beta']}")

        log_experiment.close()
        progress_bar.finish()


if __name__ == "__main__":
    Experiment2.do(Model(export_datafile="exec", test=True))
