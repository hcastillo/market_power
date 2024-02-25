#!/usr/bin/env python
# coding: utf-8
"""
ABM model calibrator, using the model
@author: hector@bith.net
"""
import random

import numpy

import util.utilities as utilities
import statistics
from market_power.model import Model
import pandas as pd
import warnings
from progress.bar import Bar
import matplotlib.pyplot as plt
import matplotlib as mpl
import os
import math
import numpy as np


class Experiment3:
    N = 100
    T = 1000
    MC = 10
    analyze_data = ['firms_Y', 'firms_A', 'firms_r']
    OUTPUT_DIRECTORY = "experiment3"
    beta = {
        # if instead of a list, you want to use a range, use np.arange(start,stop,step) to generate the list:
        # 'eta': np.arange(0.00001,0.9, 0.1) --> [0.0001, 0.1001, 0.2001... 0.9001]
        #
        'beta': [0.02, 0.05]
    }
    eta = {
        'eta': [0.0001, 0.1, 0.2, 0.25]
    }

    @staticmethod
    def color_fader(c1, c2, mix=0):  # fade (linear interpolate) from color c1 (at mix=0) to c2 (mix=1)
        c1 = np.array(mpl.colors.to_rgb(c1))
        c2 = np.array(mpl.colors.to_rgb(c2))
        return mpl.colors.to_hex((1 - mix) * c1 + mix * c2)

    @staticmethod
    def special_stats_function(model, _data):
        xx = []
        yy = []
        # # it will plot the rank of the logA of each firm in this instant model.T
        log_firm_a = [firm.A for firm in model.firms]
        log_firm_a.sort(reverse=True)
        for j in range(len(log_firm_a)):
            if log_firm_a[j] > 0:
                xx.append(math.log(log_firm_a[j]))
                yy.append(math.log(j + 1))
        plt.scatter(xx, yy, color=Experiment3.color_fader('yellow', 'blue', model.t / Experiment3.T))
        return {}


    @staticmethod
    def generate_gradient_example(description):
        plt.clf()
        plt.xlabel("t")
        plt.ylabel("color")
        for j in range(Experiment3.T):
            plt.scatter([j], [1], color=Experiment3.color_fader('yellow', 'blue', j / Experiment3.T))
        plt.savefig(description.replace(".csv", "_gradient.png"), dpi=300)

    @staticmethod
    def manage_stats_options(model):
        model.statistics.add(what="firms", name="Y", prepend=" ", logarithm=True)
        model.statistics.add(what="firms", name="A", prepend=" ", logarithm=True)
        model.statistics.add(what="firms", name="r", prepend=" ", function=statistics.mean)


    @staticmethod
    def run_model(model: Model, description, values, create_gradient_plot=False):
        values["T"] = Experiment3.T
        values["N"] = Experiment3.N
        model.statistics.interactive = False
        model.configure(**values)
        model.statistics.define_output_directory(Experiment3.OUTPUT_DIRECTORY)
        Experiment3.manage_stats_options(model)
        if create_gradient_plot:
            plt.clf()
            plt.xlabel("log firm_a")
            plt.ylabel("log rank")
            model.statistics.external_function_to_obtain_stats = Experiment3.special_stats_function
        else:
            model.statistics.external_function_to_obtain_stats = None
        data, _ = model.run(export_datafile=description)
        if create_gradient_plot:
            plt.savefig(description.replace(".csv","_gradient.png"), dpi=300)
        return data

    @staticmethod
    def plot(array_with_data, array_with_x_values, title, title_x, filename):
        for i in array_with_data:
            mean = []
            standard_deviation = []
            for j in array_with_data[i]:
                # mean is 0, std is 1:
                mean.append(j[0])
                standard_deviation.append(j[1] / 2)
            plt.clf()
            plt.title(title)
            plt.xlabel(title_x)
            plt.ylabel(f"{i}")
            plt.errorbar(array_with_x_values, mean, standard_deviation, linestyle='None', marker='^')
            plt.savefig(f"{filename}_{i}.png", dpi=300)

    @staticmethod
    def plot_ddf(array_with_data, title, filename):
        xx = []
        yy = []
        sorted = array_with_data['firms_A'].sort_values(ascending=False)
        j = 1
        for i in sorted:
            if not numpy.isnan(i) and i > 0:
                xx.append(math.log(i))
                yy.append(math.log(j))
                j += 1
        plt.plot(xx, yy, "ro")
        plt.savefig(f"{filename}_ddf.png", dpi=300)

    @staticmethod
    def get_num_models(parameters):
        return len(list(Experiment3.get_models(parameters)))

    @staticmethod
    def get_models(parameters):
        return utilities.cartesian_product(parameters)

    @staticmethod
    def do(model: Model):
        if not os.path.isdir(Experiment3.OUTPUT_DIRECTORY):
            os.mkdir(Experiment3.OUTPUT_DIRECTORY)
        log_experiment = open(f'{Experiment3.OUTPUT_DIRECTORY}/experiment3.txt', 'w')
        num_models_analyzed = 0
        model.test = False

        progress_bar = Bar('Executing models', max=Experiment3.get_num_models(Experiment3.beta) *
                                                   Experiment3.get_num_models(Experiment3.eta))
        progress_bar.update()
        Experiment3.generate_gradient_example(f"{Experiment3.OUTPUT_DIRECTORY}/experiment3.csv")
        for beta in Experiment3.get_models(Experiment3.beta):
            results_to_plot = {}
            results_x_axis = []
            for eta in Experiment3.get_models(Experiment3.eta):
                values = beta.copy()
                values.update(eta)
                result_iteration = pd.DataFrame()
                aborted_models = 0
                for i in range(Experiment3.MC):
                    mc_iteration = random.randint(9999, 20000)
                    values['default_seed'] = mc_iteration
                    result_mc = Experiment3.run_model(model,
                                                      f"{Experiment3.OUTPUT_DIRECTORY}/experiment3_{num_models_analyzed}_{i}",
                                                      values, i==0)
                    if len(result_mc) != Experiment3.T:
                        aborted_models += 1
                    result_iteration = pd.concat([result_iteration, result_mc])
                Experiment3.plot_ddf(result_iteration, f"{beta}{eta}",
                                     f"{Experiment3.OUTPUT_DIRECTORY}/experiment3_{num_models_analyzed}_{i}")
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
                    result_iteration_values = (f"aborted_models={aborted_models}/{Experiment3.MC} "
                                               + result_iteration_values)
                print(f"model #{num_models_analyzed}: {values}: {result_iteration_values}", file=log_experiment)
                num_models_analyzed += 1
                progress_bar.next()
            Experiment3.plot(results_to_plot, results_x_axis, beta, "eta",
                             f"{Experiment3.OUTPUT_DIRECTORY}/beta{beta['beta']}")

        log_experiment.close()
        progress_bar.finish()


if __name__ == "__main__":
    Experiment3.do(Model(export_datafile="exec", test=True))
