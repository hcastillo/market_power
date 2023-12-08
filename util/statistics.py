#!/usr/bin/env python
# coding: utf-8
"""
ABM model auxiliary file: to have statistics and plot
@author:  hector@bith.net
"""
from progress.bar import Bar

from market_power.bank import BankSector
from util.log import Log
from util.stats_array import StatsFirms, StatsBankSector
import os

class Statistics:
    OUTPUT_DIRECTORY = "output"

    # This time the idea is to use pandas to store the statistics
    def __init__(self, its_model):
        self.model = its_model
        self.data = {}
        self.plot_min = 0
        self.plot_max = None
        self.plot_what = []
        import os
        if not os.path.isdir(self.OUTPUT_DIRECTORY):
            os.mkdir(self.OUTPUT_DIRECTORY)
        self.export_datafile = None
        self.export_description = None
        self.do_plot = False
        self.interactive = True

    def info_status(self, before_start=False):
        for firm in self.model.firms:
            self.model.log.info_firm(firm, before_start=before_start)

    def current_status_save(self):
        # it returns also a string with the status
        result = ""
        for item in self.data:
            result += self.data[item].store_statistics()
        return result

    def add(self, what, name, prepend="", symbol=None, attr_name=None, number_type=float, function=sum,
            repr_function="Σ", plot=True, logarithm=False, show=True):
        if not attr_name:
            attr_name = name
        if not symbol:
            symbol = name.replace(" ", "_")
            if len(symbol) != len(name):
                symbol = symbol.lower()
        if not symbol.isascii():
            symbol = name
        if not callable(function):
            raise TypeError("function parameter should be a callable type")
        if what == BankSector:
            self.data["bank_" + name.replace(" ", "_")] = StatsBankSector(self.model, number_type, name, symbol,
                                                                          prepend=prepend, plot=plot,
                                                                          attr_name=attr_name, logarithm=logarithm,
                                                                          show=show)
        else:
            self.data["firms_" + name.replace(" ", "_")] = StatsFirms(self.model, number_type, name, symbol,
                                                                      prepend=prepend, function=function,
                                                                      repr_function=repr_function,
                                                                      plot=plot, attr_name=attr_name,
                                                                      logarithm=logarithm, show=show)

    def get_export_path(self, filename):
        if not filename.startswith(Statistics.OUTPUT_DIRECTORY):
            filename = f"{Statistics.OUTPUT_DIRECTORY}/{self.model.get_id_for_filename()}{filename}"
        else:
            filename = f"{self.model.get_id_for_filename()}{filename}"
        return filename if filename.endswith('.txt') else f"{filename}.txt"

    def export_data(self, export_datafile=None, export_description=None):
        if export_datafile:
            if self.interactive:
                progress_bar = Bar('Saving output in ' + self.get_export_path(export_datafile),
                                   max=self.model.config.T)
            else:
                progress_bar = None
            with open(export_datafile, 'w', encoding="utf-8") as savefile:
                if export_description:
                    savefile.write(f"# {export_description}\n")
                else:
                    savefile.write(f"# {__name__} T={self.model.config.T} N={self.model.config.N}\n")
                header = " t"
                for item in self.data:
                    header += "\t" + self.data[item].__str__()
                savefile.write(header + "\n")
                for i in range(self.model.config.T):
                    line = f"{i:3}"
                    for item in self.data:
                        line += "\t" + self.data[item][i]
                    savefile.write(line + "\n")
                    if progress_bar:
                        progress_bar.next()
            if progress_bar:
                progress_bar.finish()

    def plot(self, results_multiple=None):
        if self.do_plot:
            if self.plot_what:
                what_to_plot = 0
                for item in self.data:
                    if item in self.plot_what:
                        what_to_plot += 1
            else:
                what_to_plot = len(self.data)
            plotted_files = []
            text = f"Saving {self.do_plot} plots"
            if self.interactive:
                progress_bar = Bar(f"{text} in {self.OUTPUT_DIRECTORY}/{self.model.get_id_for_filename()}*",
                                   max=what_to_plot)
            else:
                progress_bar = None
            for item in self.data:
                if not self.plot_what or item in self.plot_what:
                    if results_multiple:
                        plotted_files.append(self.data[item].plot(plot_format=self.do_plot,
                                                                  plot_min=self.plot_min, plot_max=self.plot_max,
                                                                  multiple=results_multiple, multiple_key=item))
                    else:
                        plotted_files.append(self.data[item].plot(plot_format=self.do_plot,
                                                                  plot_min=self.plot_min, plot_max=self.plot_max))
                    if progress_bar:
                        progress_bar.next()

            if progress_bar:
                progress_bar.finish()
            if results_multiple or not self.model.statistics.multiple:
                self.execute_program(plotted_files)

    def execute_program(self, plot_format_array):
        if plot_format_array.count(None) > 0:
            plot_format_array.remove(None)
        if len(plot_format_array) == 1 and self.model.statistics.interactive:
            import configparser
            config = configparser.ConfigParser()
            config_file = 'market_power.config'
            config.read(config_file)
            file_extension = plot_format_array[0][-3:]
            if file_extension in config:
                if 'program' in config[file_extension]:
                    executable = config[file_extension]['program']
                    if executable.lower() == "default":
                        import os
                        if os.name == 'nt':
                            plot_format_array[0] = plot_format_array[0].replace('/', '\\')
                        os.startfile(plot_format_array[0], 'open')
                    else:
                        import subprocess
                        import os.path
                        if os.path.exists(executable):
                            subprocess.run([executable, plot_format_array[0]], stdout=subprocess.DEVNULL, shell=True)

    def get_what(self):
        print(self.model.log.colors.remark(f"\t{'name':20} Σ=summation ¯=average, Ξ=logarithm scale"))
        for item in self.data:
            print(f"\t{item:20} {self.data[item].get_description()}")

    def get_plot_formats(self, display: bool = False):
        if display:
            print(self.model.log.colors.remark(f"\t{'name':20} "))
            for item in StatsBankSector.get_plot_formats():
                print(f"\t{item}")
        else:
            return StatsBankSector.get_plot_formats()

    def enable_plotting(self, plot_format: str, plot_min: int = None, plot_max: int = None, plot_what: str = ""):
        self.do_plot = plot_format
        if plot_min and plot_min >= 0:
            self.plot_min = plot_min
        if plot_max and plot_max <= self.model.config.T:
            self.plot_max = plot_max
        self.plot_what = plot_what

    def initialize_model(self, export_datafile=None, export_description=None):
        self.export_datafile = export_datafile
        self.export_description = export_description
        if self.model.log.progress_bar and not self.do_plot and not self.export_datafile:
            # if no debug, and no output to file and no plots, then why you execute this?
            self.do_plot = StatsBankSector.get_plot_formats()[0]  # by default, the first one type
            self.model.log.warning("--plot enabled due to lack of any output", before_start=True)
        if not self.model.test:
            self.info_status(before_start=True)

    def finish_model(self, export_datafile=None, export_description=None):
        if not self.model.test:
            self.export_data(export_datafile=export_datafile, export_description=export_description)
            self.plot()

    def clear_output_dir(self):
        for file in [f for f in os.listdir(self.OUTPUT_DIRECTORY)]:
            if os.path.isfile(self.OUTPUT_DIRECTORY+"/"+file):
                self.model.log.warning(f"Removing {self.OUTPUT_DIRECTORY+'/'+file}", before_start=True)
                os.remove(self.OUTPUT_DIRECTORY+"/"+file)


def mean(data):
    """ returns the mean of an array"""
    result = i = 0
    for i, x in enumerate(data):
        result += x
    return result / i



def allvalues(data):
    result = []
    for i in enumerate(data):
        result.append(i)
    return result
