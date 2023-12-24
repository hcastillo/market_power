#!/usr/bin/env python
# coding: utf-8
"""
ABM model auxiliary file: to have statistics and plot
@author:  hector@bith.net
"""
from progress.bar import Bar
from util.stats_array import StatsFirms, StatsBankSector, StatsSpecificFirm, PlotMethods
import os
import subprocess


class Statistics:
    OUTPUT_DIRECTORY = "output"

    # This time the idea is to use pandas to store the statistics
    def __init__(self, its_model):
        self.model = its_model
        self.data = {}
        self.plot_min = 0
        self.multiple = False
        self.plot_max = None
        self.plot_what = []
        if not os.path.isdir(self.OUTPUT_DIRECTORY):
            os.mkdir(self.OUTPUT_DIRECTORY)
        self.export_datafile = None
        self.export_description = None
        self.do_plot = False
        self.interactive = True
        self.readable_file_format = False
        self.export_datafile_fields_separator = ","
        self.export_datafile_extension = ".csv"

    def set_file_readable(self):
        self.readable_file_format = True
        self.export_datafile_extension = ".txt"
        if self.model.export_datafile:
            self.model.export_datafile = self.model.export_datafile.replace(".csv",".txt")

    def info_status(self, before_start=False):
        for firm in self.model.firms:
            self.model.log.info_firm(firm, before_start=before_start)

    def current_status_save(self):
        # it returns also a string with the status
        result = ""
        for item in self.data:
            current_value = self.data[item].get_statistics()
            if self.model.log.only_firms_or_bank:
                if self.data[item].its_name.lower() == self.model.log.only_firms_or_bank.lower():
                    result += current_value
            else:
                result += current_value
        return result

    def current_status_save_after_failed_firms_removed(self):
        result = ""
        for item in self.data:
            if self.data[item].its_name.lower() == "firms" and self.data[item].description != "failures":
                result += self.data[item].get_statistics(store=False)
        return result.replace("firms ", "      ")

    def add(self, what, name, prepend="", symbol=None, attr_name=None, number_type=float, function=sum,
            repr_function="Σ", plot=True, logarithm=False, show=True):
        if not attr_name:
            attr_name = name
        if not symbol:
            symbol = name.replace(" ", "_")
            if len(symbol) != len(name):
                symbol = symbol.lower()
        # if not symbol.isascii():
        #    symbol = name
        if not callable(function):
            raise TypeError("function parameter should be a callable type")
        if what == "bank":
            self.data["bank_" + name.replace(" ", "_")] = StatsBankSector(self.model, number_type, name, symbol,
                                                                          prepend=prepend, plot=plot,
                                                                          attr_name=attr_name, logarithm=logarithm,
                                                                          show=show)
        elif what == "firms":
            self.data["firms_" + name.replace(" ", "_")] = StatsFirms(self.model, number_type, name, symbol,
                                                                      prepend=prepend, function=function,
                                                                      repr_function=repr_function,
                                                                      plot=plot, attr_name=attr_name,
                                                                      logarithm=logarithm, show=show)
        else:
            try:
                num_firm = int(what.replace("firm_", ""))
            except ValueError:
                raise ValueError(f"invalid number: I expected a text as firmX with X=[0..{self.model.config.N - 1}]")
            if num_firm < 0 or num_firm >= self.model.config.N:
                raise ValueError(f"invalid number: should be [0..{self.model.config.N - 1}]")
            self.data[what + "_" + name] = StatsSpecificFirm(self.model, number_type, name, symbol,
                                                             prepend=prepend, plot=plot, attr_name=attr_name,
                                                             logarithm=logarithm, show=show, firm_number=num_firm)

    def get_export_path(self, filename):
        if not filename.startswith(Statistics.OUTPUT_DIRECTORY):
            filename = f"{Statistics.OUTPUT_DIRECTORY}/{self.model.get_id_for_filename()}{filename}"
        else:
            filename = f"{self.model.get_id_for_filename()}{filename}"
        return filename if filename.endswith(self.export_datafile_extension) \
                           else f"{filename}{self.export_datafile_extension}"

    def export_data(self, export_datafile=None, export_description=None):
        if export_datafile:
            if self.interactive:
                progress_bar = Bar('Saving output in ' + self.get_export_path(export_datafile),
                                   max=self.model.config.T)
            else:
                progress_bar = None
            with (open(export_datafile, 'w', encoding="utf-8") as save_file):
                if export_description:
                    save_file.write(f"# {export_description}\n")
                else:
                    save_file.write(f"# {__name__} T={self.model.config.T} N={self.model.config.N}\n")
                header = "  t"
                for item in self.data:
                    if self.model.model_id:
                        header += self._format_field(self.data[item].name_for_files() + f"_{self.model.model_id}")
                    else:
                        header += self._format_field(self.data[item].name_for_files())
                save_file.write(header + "\n")
                for i in range(self.model.config.T):
                    line = f"{i:>3}"
                    for item in self.data:
                        # line += f"{self.file_fields_separator}{self.data[item].data[i]}"
                        line += self._format_value(item, i)
                    save_file.write(line + "\n")
                    if progress_bar:
                        progress_bar.next()
            if progress_bar:
                progress_bar.finish()

    def _format_field(self, value):
        if self.readable_file_format:
            return f"  {value:>10}"
        else:
            return f"{self.export_datafile_fields_separator}{value}"

    def _format_value(self, item, position):
        if self.readable_file_format:
            return self._format_field(self.data[item][position])
        else:
            return self._format_field(self.data[item].data[position])

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

            if self.do_plot == PlotMethods.gretl:
                plotted_files.append(self.data[list(self.data.keys())[0]].plot(plot_format=self.do_plot,
                                                                               plot_min=self.plot_min,
                                                                               plot_max=self.plot_max, generic=True))

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
                        if os.name == 'nt':
                            plot_format_array[0] = plot_format_array[0].replace('/', '\\')
                        os.startfile(plot_format_array[0], 'open')
                    else:
                        if os.path.exists(executable):
                            subprocess.run([executable, plot_format_array[0]], stdout=subprocess.DEVNULL, shell=True)

    def get_what(self):
        print(self.model.log.colors.remark(f"\t{'name':20} Σ=summation ¯=average, Ξ=logarithm scale"))
        for item in self.data:
            print(f"\t{item:20} {self.data[item].get_description()}")

    def get_default_plot_method(self):
        return PlotMethods('default')

    def enable_plotting(self, plot_format: PlotMethods, plot_min: int = None, plot_max: int = None,
                        plot_what: str = ""):
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
            self.do_plot = self.get_default_plot_method()
            self.model.log.warning("--plot enabled due to lack of any output", before_start=True)
        if not self.model.test:
            self.model.log.step(self.current_status_save(), before_start=True)

    def finish_model(self, export_datafile=None, export_description=None):
        if not self.model.test:
            self.remove_not_used_data_after_abortion()
            self.export_data(export_datafile=export_datafile, export_description=export_description)
            self.plot()

    def clear_output_dir(self):
        for file in [f for f in os.listdir(self.OUTPUT_DIRECTORY)]:
            if os.path.isfile(self.OUTPUT_DIRECTORY + "/" + file):
                self.model.log.info(f"Removing {self.OUTPUT_DIRECTORY + '/' + file}", before_start=True)
                os.remove(self.OUTPUT_DIRECTORY + "/" + file)

    def remove_not_used_data_after_abortion(self):
        if self.model.abort_execution:
            self.model.config.T = self.model.t
            for item in self.model.statistics.data:
                self.model.statistics.data[item].data = self.model.statistics.data[item].data[:self.model.t + 1]


def mean(data):
    """ returns the mean of an array"""
    result = i = 0
    for i, x in enumerate(data):
        result += x
    return result / i


def _mode_of_a_list(array):
    most = max(list(map(array.count, array)))
    return list(set(filter(lambda x: array.count(x) == most, array)))


def mode(data):
    to_list = []
    for _, x in enumerate(data):
        to_list.append(round(x, 1))
    return _mode_of_a_list(to_list)[0]


def all_values(data):
    result = []
    for i in enumerate(data):
        result.append(i)
    return result
