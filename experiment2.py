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
import os, sys
import math
import argparse
import scipy
import glob, shutil


class Experiment2:
    N = 100
    T = 1000
    MC = 10
    analyze_data = ['firms_Y', 'firms_A', 'bank_A', 'firms_r']
    OUTPUT_DIRECTORY = "experiment2"
    number_of_tries_in_case_of_abort = 3
    parameters_not_eta = {
        # if instead of a list, you want to use a range, use np.arange(start,stop,step) to generate the list:
        # 'eta': np.arange(0.00001,0.9, 0.1) --> [0.0001, 0.1001, 0.2001... 0.9001]
        #
        'beta': [0.02, 0.03, 0.04, 0.05],
        'g': [1.0, 1.1, 1.2],
        'k': [1.0, 1.1, 1.2],
        'w': [0.5, 0.6, 0.7]
    }
    eta = {
        'eta': [0.0001, 0.1, 0.3]
    }

    @staticmethod
    def manage_stats_options(model):
        model.statistics.add(what="bank", name="L", prepend="bank    ")
        model.statistics.add(what="bank", name="A", prepend=" | ", logarithm=True)
        model.statistics.add(what="bank", name="D", prepend="  ")
        model.statistics.add(what="bank", name="profits", symbol="π", prepend="  ", attr_name="profits")
        model.statistics.add(what="bank", name="bad debt", logarithm=True,
                             symbol="bd", prepend=" ", attr_name="bad_debt")
        model.statistics.add(what="firms", name="K", prepend="\n              firms   ", logarithm=True)
        model.statistics.add(what="firms", name="A", prepend=" |")
        model.statistics.add(what="firms", name="L", prepend=" ", logarithm=True)
        model.statistics.add(what="firms", name="profits", prepend=" ", symbol="π", attr_name="pi")
        model.statistics.add(what="firms", name="Y", prepend=" ", logarithm=True)
        model.statistics.add(what="firms", name="r", prepend=" ", function=statistics.mean)
        model.statistics.add(what="firms", name="I", prepend=" ")
        model.statistics.add(what="firms", name="gamma", prepend=" ", function=statistics.mean, symbol="γ")
        model.statistics.add(what="firms", name="u", function=statistics.mean, repr_function="¯")
        model.statistics.add(what="firms", name="desiredK", symbol="dK", show=False)
        model.statistics.add(what="firms", name="offeredL", symbol="oL", show=False, function=statistics.mean)
        model.statistics.add(what="firms", name="gap_of_L", show=False)
        model.statistics.add(what="firms", name="demandL", symbol="dL", show=False, function=statistics.mean)
        model.statistics.add(what="firms", name="failures", attr_name="failed", symbol="fail",
                             number_type=int, prepend=" ")

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
                                             plot_min=0, plot_max=Experiment2.T,
                                             plot_what='firms_Y,firms_failures,bank_bad_debt')
        number_of_tries_in_case_of_abort = Experiment2.number_of_tries_in_case_of_abort
        while number_of_tries_in_case_of_abort > 0:
            data, _ = model.run(export_datafile=description)
            if len(data) == Experiment2.T:
                # when exactly T iterations of data are returned = OK
                number_of_tries_in_case_of_abort -= 1
            else:
                # in case of aborted, we change the seed and run it again:
                model.t = 0
                model.config.default_seed += 1
                model.abort_execution = False
                model.config.T = Experiment2.T
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
            try:
                plt.errorbar(array_with_x_values, mean, standard_deviation, linestyle='None', marker='^')
            except:
                pass
            else:
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
    def get_filename_for_iteration(parameters):
        result = str(parameters)
        for r in "{}',:. ":
            result = result.replace(r, "")
        return result.replace("00001", "00")


    @staticmethod
    def check():
        for elem in glob.glob(rf'{Experiment2.OUTPUT_DIRECTORY}/*.csv'):
            other_files=elem.replace(".csv","*")
            for elem1 in glob.glob(rf'{other_files}'):
                print(elem1)
                shutil.move(elem1, Experiment2.OUTPUT_DIRECTORY + "/good")
        sys.exit(0)
        for elem in glob.glob(rf'{Experiment2.OUTPUT_DIRECTORY}/*.csv'):
            data = pd.read_csv(elem,header=2)
            coef_corr = scipy.stats.spearmanr(data.FirmsY.to_numpy(), [i for i in range(len(data))])
            coef_corr1 = scipy.stats.spearmanr(data.FirmsY[:666].to_numpy(), [i for i in range(666)])
            if coef_corr.statistic > 0.99:
                print("bad",elem, coef_corr.statistic, coef_corr1.statistic)
            elif coef_corr1.statistic > 0.999:
                print("reg",elem, coef_corr.statistic, coef_corr1.statistic)
                shutil.move(elem, Experiment2.OUTPUT_DIRECTORY + "/regular")

    @staticmethod
    def get_statistics():
        Experiment2.__verify_directories__()
        models_ok = []
        models_bad = []
        models_regular = []
        models_absent = []
        models = []
        models_iterations_num_ok = [ [] for i in range(Experiment2.MC + 1)]
        coefs = []
        coefs66= []
        gdp = []
        bad_debt = []
        for parameters_not_eta in Experiment2.get_models(Experiment2.parameters_not_eta):
            for eta in Experiment2.get_models(Experiment2.eta):
                values = parameters_not_eta.copy()
                values.update(eta)
                model_name = Experiment2.get_filename_for_iteration(values)
                num_ok = 0
                for i in range(Experiment2.MC):
                    filename_for_iteration = f"{model_name}_{i}.csv"
                    path = ""
                    if os.path.exists(f"{Experiment2.OUTPUT_DIRECTORY}/good/{filename_for_iteration}"):
                        path = f"{Experiment2.OUTPUT_DIRECTORY}/good/"
                        models_ok += [filename_for_iteration]
                        num_ok += 1
                    elif os.path.exists(f"{Experiment2.OUTPUT_DIRECTORY}/bad/{filename_for_iteration}"):
                        path = f"{Experiment2.OUTPUT_DIRECTORY}/bad/"
                        models_bad += [filename_for_iteration]
                    elif os.path.exists(f"{Experiment2.OUTPUT_DIRECTORY}/regular/{filename_for_iteration}"):
                        path = f"{Experiment2.OUTPUT_DIRECTORY}/regular/"
                        models_regular += [filename_for_iteration]
                    else:
                        models_absent += [filename_for_iteration]
                        coefs.append( None )
                        coefs66.append( None )
                    models += [ f"{model_name}_{i}" ]

                    if path:
                        data = pd.read_csv(f"{path}/{filename_for_iteration}", header=2)
                        bad_debt.append( data.BankBD.mean() )
                        gdp.append( data.FirmsY.mean() )
                        coef = scipy.stats.spearmanr(data.FirmsY.to_numpy(), [i for i in range(len(data))])
                        coefs.append( None if coef.statistic is np.nan else coef.statistic )
                        coef66 = scipy.stats.spearmanr(data.FirmsY[:666].to_numpy(), [i for i in range(666)])
                        coefs66.append( None if coef66.statistic is np.nan else coef66.statistic )

                models_iterations_num_ok[num_ok] += [model_name]

        print(f"\nnum_models_analyzed: {len(models)}")
        print(f"\tmodels_ok: {len(models_ok)}")
        print(f"\tmodels_regular: {len(models_regular)}")
        print(f"\tmodels_bad: {len(models_bad)}")
        if models_absent:
            print(f"\tmodels_absent: {len(models_absent)}")
        print("\n")
        total_considered = 0
        total_not_considered = 0
        plt.clf()
        xx = []
        yy = []
        bar_labels = []
        bar_colors = []
        for i in range(Experiment2.MC + 1):
            bar_labels.append(i)
            print(f"models_with_ #{i} bad executions=", len(models_iterations_num_ok[i]))
            this_step_ok = i * len(models_iterations_num_ok[i])
            total_considered += this_step_ok
            yy.append(len(models_iterations_num_ok[i]))
            xx.append(i)
            if i== 0:
                bar_colors.append('tab:red')
            elif i<=4:
                bar_colors.append('tab:orange')
            else:
                bar_colors.append('tab:blue')
            total_not_considered += (10 - i) * len(models_iterations_num_ok[i])
        print("total considered", total_considered)
        print("total not considered", total_not_considered)
        fig, ax = plt.subplots()
        ax.bar(xx, yy, label=bar_labels, color=bar_colors)
        ax.set_ylabel('Num of models')
        ax.set_title('Amount over 10 of models with Pearson coef>0.99')
        #ax.legend(title='Models')
        plt.savefig(Experiment2.OUTPUT_DIRECTORY+'/distribution_of_models.svg')

        with open(Experiment2.OUTPUT_DIRECTORY + "stats.py", "w") as stats_file:
            stats_file.write(f"models_analyzed = {len(models)}\n")
            stats_file.write(f"models_bad = {models_bad}\n")
            stats_file.write(f"models_regular = {models_regular}\n")
            stats_file.write(f"models_ok = {models_ok}\n")
            stats_file.write(f"data =  {{ 'pearson':{coefs}, 'pearson66':{coefs66}, 'bd':{bad_debt}, 'gdp':{gdp} }}\n")
            stats_file.write(f"models = {models}\n")
            stats_file.write(f"import pandas as pd\n")
            stats_file.write(f"df = pd.DataFrame(data, index=models)\n")
            stats_file.write(f"successive_executions_of_models_by_num = {models_iterations_num_ok}\n")

    @staticmethod
    def listnames():
        num = 0
        for parameters_not_eta in Experiment2.get_models(Experiment2.parameters_not_eta):
            for eta in Experiment2.get_models(Experiment2.eta):
                values = parameters_not_eta.copy()
                values.update(eta)
                model_name = Experiment2.get_filename_for_iteration(values)
                print(model_name)
                num += 1
        print("total: ", num)


    @staticmethod
    def __verify_directories__():
        if not os.path.isdir(Experiment2.OUTPUT_DIRECTORY):
            os.mkdir(Experiment2.OUTPUT_DIRECTORY)
        if not os.path.isdir(Experiment2.OUTPUT_DIRECTORY+"/bad"):
            os.mkdir(Experiment2.OUTPUT_DIRECTORY+"/bad")



    @staticmethod
    def __get_value_from_all_executions__(filename, parameter_to_obtain):
        result = 0
        num = 0
        std = 0
        for file in glob.glob(rf'{Experiment2.OUTPUT_DIRECTORY}/*/{filename}_*.csv'):
            data = pd.read_csv(f"{file}", header=2)
            result += data[parameter_to_obtain].mean()
            num += 1
            std += data[parameter_to_obtain].std()
        return result/num,std/num

    @staticmethod
    def plot_bankruptcy():
        i = 0
        results_y = {i: [] for i in Experiment2.eta['eta']}
        deviation_y = {i: [] for i in Experiment2.eta['eta']}
        results_x = []
        xticks = []
        for parameters_not_eta in Experiment2.get_models(Experiment2.parameters_not_eta):
            if parameters_not_eta['w'] == 0.7:
                results_x.append(i)
                for eta in Experiment2.get_models(Experiment2.eta):
                    values = parameters_not_eta.copy()
                    values.update(eta)
                    filename_for_iteration = Experiment2.get_filename_for_iteration(values)
                    eta = eta['eta']
                    fails, std = Experiment2.__get_value_from_all_executions__(filename_for_iteration, 'FirmsFAIL')
                    results_y[eta].append(fails)
                    deviation_y[eta].append(std)
                    #print(i,filename_for_iteration)
                valor_x = ""
                valor_x = f"g={values['g']}\nk={values['k']}"
                # if (x - 1) % 9 == 0:
                #     valor_x = f"g={values['g']}\nk={values['k']}"
                # if not valor and (x - 1) % 3 == 0:
                #     valor = f"k={values['k']}"
                if i % 3 == 0:
                    if values['g']==1:
                        xticks.append(f"$\\beta$={values['beta']}\ng={values['g']}")
                    else:
                        xticks.append(f"g={values['g']}")
                else:
                    xticks.append(f" ")
                i += 1
        plt.clf()
        eta_colors = {0.0001: 'r', 0.1: 'b', 0.3: 'k'}
        eta_markers = {0.0001: 'D', 0.1: '^', 0.3: 'o'}
        for eta in Experiment2.eta['eta']:
            plt.errorbar(results_x, results_y[eta], deviation_y[eta], linestyle='None', color=eta_colors[eta],
                         marker=eta_markers[eta])
        plt.xticks(range(len(xticks)), xticks, fontsize=6, rotation='vertical')
        plt.savefig(Experiment2.OUTPUT_DIRECTORY+"\\plot_bankruptcies.png")

    @staticmethod
    def plot_surface():
        # import matplotlib.pyplot as plt
        # import numpy as np
        #
        # ax = plt.figure().add_subplot(projection='3d')
        #
        # # Plot a sin curve using the x and y axes.
        # x = np.linspace(0, 1, 100)
        # y = np.sin(x * 2 * np.pi) / 2 + 0.5
        # ax.plot(x, y, zs=0, zdir='z', label='curve in (x, y)')
        #
        # # Plot scatterplot data (20 2D points per colour) on the x and z axes.
        # colors = ('r', 'g', 'b', 'k')
        #
        # # Fixing random state for reproducibility
        # np.random.seed(19680801)
        #
        # x = np.random.sample(20 * len(colors))
        # y = np.random.sample(20 * len(colors))
        # c_list = []
        # for c in colors:
        #     c_list.extend([c] * 20)
        # # By using zdir='y', the y value of these points is fixed to the zs value 0
        # # and the (x, y) points are plotted on the x and z axes.
        # ax.scatter(x, y, zs=0, zdir='y', c=c_list, label='points in (x, z)')
        #
        # # Make legend, set axes limits and labels
        # ax.legend()
        # ax.set_xlim(0, 1)
        # ax.set_ylim(0, 1)
        # ax.set_zlim(0, 1)
        # ax.set_xlabel('X')
        # ax.set_ylabel('Y')
        # ax.set_zlabel('Z')
        #
        # # Customize the view angle so it's easier to see that the scatter points lie
        # # on the plane y=0
        # ax.view_init(elev=20., azim=-35, roll=0)
        #
        # plt.show()
        from experiment2stats import data,models,successive_executions_of_models_by_num
        from colour import Color
        import math
        red = Color("red")
        gradation_colors = list(red.range_to(Color("green"), 11))
        xx = []
        yy = []
        zz = []
        xticks = []
        colors = []
        yticks = []
        xticks1 = []
        xticks2 = []
        sizes = []
        num = 0
        x = 0
        y = 0
        for beta in Experiment2.parameters_not_eta.pop('beta'):
            for eta in Experiment2.get_models(Experiment2.eta):
                for parameters_not_eta_beta in Experiment2.get_models(Experiment2.parameters_not_eta):
                    values = {'beta': beta}
                    values.update(parameters_not_eta_beta)
                    values.update(eta)
                    parameters_eta_beta = eta.copy()
                    parameters_eta_beta.update({'beta': beta})
                    filename_for_iteration = Experiment2.get_filename_for_iteration(values)
                    name_x = Experiment2.get_filename_for_iteration(parameters_not_eta_beta)
                    name_y = Experiment2.get_filename_for_iteration(
                        parameters_eta_beta)  # .replace('beta00','b').replace('eta0','e')
                    xx.append(x)
                    yy.append(y)
                    for i in range(11):
                        if filename_for_iteration in successive_executions_of_models_by_num[i]:
                            colors.append(gradation_colors[i].get_hex())

                    gdp = 0
                    bad_debt = 0
                    for i in range(Experiment2.MC):
                        index = models.index( f"{filename_for_iteration}_{i}")
                        gdp += data['gdp'][index]
                        bad_debt += data['bd'][index]
                    gdp /= Experiment2.MC
                    bad_debt /= Experiment2.MC
                    zz.append(math.log(gdp))
                    sizes.append(math.log(bad_debt))
                    num += 1
                    x += 1
                    if y == 0:
                        valor = ""
                        if (x - 1) % 9 == 0:
                            valor = f"g={values['g']}\nk={values['k']}"
                        if not valor and (x - 1) % 3 == 0:
                            valor = f"k={values['k']}"
                        xticks.append(valor)
                        xticks1.append(name_x)
                        xticks2.append(f"w={values['w']}")
                y += 1
                yticks.append(name_y)
                x = 0
        plt.clf()
        size_min=min(sizes)
        size_max=max(sizes)
        size_step=(size_max-size_min)/99
        for i in range(len(sizes)):
            sizes[i] = (sizes[i]-size_min)/size_step
        ax = plt.figure().add_subplot(projection='3d')
        ax.scatter(xx, yy, zz, c=colors, s=sizes)
        # ax.scatter(xx,yy,zz, zdir='y', c=colors, s=sizes, label='points in (x, z)')
        # Make legend, set axes limits and labels
        ax.legend()
        # ax.set_xlabel('X')
        # ax.set_ylabel('Y')
        ax.set_zlabel('ln(GDP)')
        # Customize the view angle so it's easier to see that the scatter points lie
        # on the plane y=0
        ax.set(xlim=(-1, 27), ylim=(-1, 12),zlim=(min(zz),max(zz)))
        for i in range(len(xticks)):
            # ax.annotate(xticks1[i],(i,1),rotation='vertical')
            ax.annotate(xticks2[i], (i, -1), fontsize=6)
        plt.xticks(range(len(xticks)), xticks, fontsize=6, rotation= -45)
        plt.yticks(range(len(yticks)), yticks, fontsize=6, rotation=15)
        ax.view_init(elev=10., azim=55, roll=0)
        plt.savefig(f'{Experiment2.OUTPUT_DIRECTORY}/plot_3d.png')


    @staticmethod
    def plot_points():

        from experiment2stats import successive_executions_of_models_by_num
        from colour import Color
        red = Color("red")
        gradation_colors = list(red.range_to(Color("green"), 11))
        xx = []
        yy = []
        xticks = []
        colors = []
        yticks = []
        xticks1= []
        xticks2= []
        sizes = []
        num = 0
        x=0
        y=0
        for beta in Experiment2.parameters_not_eta.pop('beta'):
            for eta in Experiment2.get_models(Experiment2.eta):
                for parameters_not_eta_beta in Experiment2.get_models(Experiment2.parameters_not_eta):
                    values = { 'beta' : beta }
                    values.update( parameters_not_eta_beta )
                    values.update(eta)
                    parameters_eta_beta = eta.copy()
                    parameters_eta_beta.update( {'beta':beta })
                    filename_for_iteration = Experiment2.get_filename_for_iteration(values)
                    name_x = Experiment2.get_filename_for_iteration(parameters_not_eta_beta)
                    name_y = Experiment2.get_filename_for_iteration(parameters_eta_beta) #.replace('beta00','b').replace('eta0','e')
                    xx.append(x)
                    yy.append(y)

                    for i in range(11):
                        if filename_for_iteration in successive_executions_of_models_by_num[i]:
                            colors.append(gradation_colors[i].get_hex())
                            sizes.append( 1+i*2 )
                    # if os.path.exists(f"{Experiment2.OUTPUT_DIRECTORY}/good/{filename_for_iteration}.csv"):
                    #     colors.append('tab:green')
                    # elif os.path.exists(f"{Experiment2.OUTPUT_DIRECTORY}/bad/{filename_for_iteration}.csv"):
                    #     colors.append('tab:red')
                    # else:
                    #     print(f"{Experiment2.OUTPUT_DIRECTORY}/bad/{filename_for_iteration}.csv")
                    #     colors.append('tab:orange')
                    num +=1
                    x += 1
                    if y==0:
                        valor = ""
                        if  (x-1) % 9 == 0:
                            valor = f"g={values['g']}\nk={values['k']}"
                        if not valor and (x-1) % 3 == 0:
                            valor = f"k={values['k']}"
                        xticks.append( valor )
                        xticks1.append(name_x)
                        xticks2.append(f"w={values['w']}")
                y+=1
                yticks.append(name_y)
                x=0
        plt.clf()
        #plt.style.use('_mpl-gallery')
        fig, ax = plt.subplots()
        ax.scatter(xx, yy, c=colors, s=sizes, vmin=0, vmax=25)
        ax.set(xlim=(-1, 27), ylim=(-1, 12))
        for i in range(len(xticks)):
            #ax.annotate(xticks1[i],(i,1),rotation='vertical')
            ax.annotate(xticks2[i], (i,-1), rotation='vertical', fontsize=6)

        plt.xticks(range(len(xticks)),xticks, fontsize=6, rotation='vertical')
        plt.yticks(range(len(yticks)),yticks, fontsize=6)
        plt.savefig(f'{Experiment2.OUTPUT_DIRECTORY}/plot_valid_models.png')

    @staticmethod
    def do(model: Model):
        Experiment2.__verify_directories__()
        num_models_analyzed = 0
        log_experiment = open(f'{Experiment2.OUTPUT_DIRECTORY}/experiment2.txt', 'a')
        model.test = False
        progress_bar = Bar('Executing models', max=Experiment2.get_num_models(Experiment2.parameters_not_eta) *
                                                         Experiment2.get_num_models(Experiment2.eta))
        progress_bar.update()
        for parameters_not_eta in Experiment2.get_models(Experiment2.parameters_not_eta):
            results_to_plot = {}
            results_x_axis = []
            for eta in Experiment2.get_models(Experiment2.eta):
                values = parameters_not_eta.copy()
                values.update(eta)
                filename_for_iteration = Experiment2.get_filename_for_iteration(values)

                if os.path.exists(f"{Experiment2.OUTPUT_DIRECTORY}/{filename_for_iteration}_ddf.png") or \
                   os.path.exists(f"{Experiment2.OUTPUT_DIRECTORY}/bad/{filename_for_iteration}_ddf.png"):
                    progress_bar.next()
                    continue

                result_iteration = pd.DataFrame()
                aborted_models = 0
                for i in range(Experiment2.MC):
                    model_was_aborted = False
                    mc_iteration = random.randint(9999, 20000)
                    values['default_seed'] = mc_iteration
                    result_mc = Experiment2.run_model(model,
                                                      f"{Experiment2.OUTPUT_DIRECTORY}/{filename_for_iteration}_{i}",
                                                      values)
                    # rare, but still possible: we try 3 times with diff seed if aborted inside run_model
                    if len(result_mc) != Experiment2.T:
                        aborted_models += 1
                        model_was_aborted = True
                    result_iteration = pd.concat([result_iteration, result_mc])
                    coef_corr = scipy.stats.spearmanr(result_mc.firms_Y.to_numpy(), [i for i in range(len(result_mc))])
                    if coef_corr.statistic > 0.99 or model_was_aborted:
                        # plot of Y is a straight line, no shocks so this model is useless:
                        # also if the model was aborted
                        for file in glob.glob(rf'{Experiment2.OUTPUT_DIRECTORY}/{filename_for_iteration}_{i}*'):
                            try:
                                shutil.move(file, Experiment2.OUTPUT_DIRECTORY+"/bad")
                            except:
                                pass

                Experiment2.plot_ddf(result_iteration, f"{parameters_not_eta}{eta}",
                                     f"{Experiment2.OUTPUT_DIRECTORY}/{filename_for_iteration}")
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
                print(f"model #{num_models_analyzed} {filename_for_iteration}: {values}: {result_iteration_values}",
                                file=log_experiment)
                num_models_analyzed += 1
                progress_bar.next()
            Experiment2.plot(results_to_plot, results_x_axis, parameters_not_eta, "eta",
                             f"{Experiment2.OUTPUT_DIRECTORY}/beta{parameters_not_eta['beta']}")

        log_experiment.close()
        progress_bar.finish()



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check ABM parameters")
    parser.add_argument('--check', default=False, action=argparse.BooleanOptionalAction,
                        help="View if all combinations are computed")
    parser.add_argument('--do', default=False, action=argparse.BooleanOptionalAction,
                        help="Execute the experiment")
    parser.add_argument('--plot_points', default=False, action=argparse.BooleanOptionalAction,
                        help="Plot the poins matrix")
    parser.add_argument('--plot_bankruptcy', default=False, action=argparse.BooleanOptionalAction,
                        help="Plot bankruptcy average")
    parser.add_argument('--plot_surface', default=False, action=argparse.BooleanOptionalAction,
                        help="Plot the GPD of all models in 3D")
    parser.add_argument('--statistics', default=False, action=argparse.BooleanOptionalAction,
                        help=f"Generate {Experiment2.OUTPUT_DIRECTORY}\statistics.py")
    parser.add_argument('--listnames', default=False, action=argparse.BooleanOptionalAction,
                        help="Print combinations to generate")
    args = parser.parse_args()
    if args.check:
        Experiment2.check()
    elif args.listnames:
        Experiment2.listnames()
    elif args.statistics:
        Experiment2.get_statistics()
    elif args.plot_points:
        Experiment2.plot_points()
    elif args.plot_surface:
        Experiment2.plot_surface()
    elif args.plot_bankruptcy:
        Experiment2.plot_bankruptcy()
    elif args.do:
        Experiment2.do(Model(export_datafile="exec", test=True))
