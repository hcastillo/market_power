#!/usr/bin/env python
# coding: utf-8
"""
ABM model auxiliary file: to have statistics and plot
@author:  hector@bith.net
"""
import os
import subprocess
from progress.bar import Bar
from util.stats_array import StatsFirms, StatsBankSector, StatsSpecificFirm, StatsSpecificData, PlotMethods
import pandas as pd


class Stats:
    OUTPUT_DIRECTORY = "output"

    def __init__(self, its_model):
        self.model = its_model
        self.dataframe = pd.DataFrame([])
        self.stats_items = {}
        self.external_function_to_obtain_stats = None
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
        if self.export_datafile:
            self.export_datafile = self.export_datafile.replace(".csv", ".txt")

    def info_status(self, before_start=False):
        for firm in self.model.firms:
            self.model.log.info_firm(firm, before_start=before_start)

    def current_status_save(self):
        # it returns also a string with the status
        result = ""
        for item in self.stats_items:
            current_value = self.stats_items[item].get_statistics()
            if not self.model.log.what_keywords or item in self.model.log.what_keywords:
                result += current_value

        # if it is defined an external function, it will receive the data to analyze it:
        if self.external_function_to_obtain_stats:
            for item, value in self.external_function_to_obtain_stats(self.model, self.stats_items).items():
                if item not in self.stats_items:
                    self.stats_items[item] = StatsSpecificData(self.model, item)
                self.dataframe[item][self.model.t] = value
        return result

    def current_status_save_after_failed_firms_removed(self):
        result = ""
        for item in self.stats_items:
            if self.stats_items[item].its_name.lower() == "firms" and self.stats_items[item].description != "failures":
                # the number of failures it's OK, what we need is to obtain the statistics again of the firms:
                result += self.stats_items[item].get_statistics(store=False)
        return result.replace("firms ", "      ")

    def add(self, what, name, prepend="", symbol=None, attr_name=None, function=sum,
            repr_function="Σ", number_type=float, plot=True, logarithm=False, show=True):
        if not attr_name:
            attr_name = name
        if not symbol:
            symbol = name.replace(" ", "_")
            if len(symbol) != len(name):
                symbol = symbol.lower()
        if not callable(function):
            raise TypeError("function parameter should be a callable type")
        if what == "bank":
            self.stats_items["bank_" + name.replace(" ", "_")] = StatsBankSector(self.model, name, symbol,
                                                                                 prepend=prepend, plot=plot,
                                                                                 number_type=number_type,
                                                                                 attr_name=attr_name,
                                                                                 logarithm=logarithm,
                                                                                 show=show,
                                                                                 column_name="bank_" +
                                                                                              name.replace(" ", "_"))
        elif what == "firms":
            self.stats_items["firms_" + name.replace(" ", "_")] = StatsFirms(self.model, name, symbol,
                                                                             prepend=prepend, function=function,
                                                                             repr_function=repr_function,
                                                                             number_type=number_type,
                                                                             plot=plot, attr_name=attr_name,
                                                                             logarithm=logarithm,
                                                                             column_name="firms_" +
                                                                                         name.replace(" ", "_"),
                                                                             show=show)
        else:
            try:
                num_firm = int(what.replace("firm_", ""))
            except ValueError:
                raise ValueError(f"invalid number: I expected a text as firmX with X=[0..{self.model.config.N - 1}]")
            if num_firm < 0 or num_firm >= self.model.config.N:
                raise ValueError(f"invalid number: should be [0..{self.model.config.N - 1}]")
            self.stats_items[what + "_" + name] = StatsSpecificFirm(self.model, name, symbol,
                                                                    prepend=prepend, plot=plot, attr_name=attr_name,
                                                                    logarithm=logarithm, show=show,
                                                                    number_type=number_type,
                                                                    column_name=what + "_" + name,
                                                                    firm_number=num_firm)

    def get_export_path(self):
        return f"{self.OUTPUT_DIRECTORY}/{self.export_datafile}{self.export_datafile_extension}"

    def determine_export_location(self):
        if self.export_datafile:
            filename = os.path.basename(self.export_datafile)
            if filename.endswith(self.export_datafile_extension):
                filename = filename[:-len(self.export_datafile_extension)]
            self.export_datafile = filename + self.model.get_id_for_export()

    def export_data(self):
        if self.export_datafile:
            if self.interactive:
                progress_bar = Bar('Saving output in ' + self.get_export_path(),
                                   max=self.model.config.T)
                progress_bar.update()
            else:
                progress_bar = None
            with (open(self.get_export_path(), 'w', encoding="utf-8") as save_file):
                if self.export_description:
                    save_file.write(f"# {self.export_description}\n")
                else:
                    save_file.write(f"# {__name__} T={self.model.config.T} N={self.model.config.N}\n")
                save_file.write(f"# pd.read_csv('{self.export_datafile}" +
                                f"{self.export_datafile_extension}',header=2)\n")
                header = "  t"
                for item in self.stats_items:
                    header += self._format_field(self.stats_items[item].name_for_files()+self.model.get_id_for_export())
                save_file.write(header + "\n")
                for i in range(self.model.config.T):
                    line = f"{i:>3}"
                    for item in self.stats_items:
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
            return self._format_field(self.stats_items[item][position])
        else:
            return self._format_field(self.dataframe[item][position])

    def plot(self, results_multiple=None):
        if self.do_plot:
            if self.plot_what:
                what_to_plot = 0
                for item in self.stats_items:
                    if item in self.plot_what:
                        what_to_plot += 1
            else:
                what_to_plot = len(self.stats_items)
            plotted_files = []
            text = f"Saving {self.do_plot} plots"
            if self.interactive:
                progress_bar = Bar(f"{text} in {self.OUTPUT_DIRECTORY}/{self.model.get_id_for_export()}*",
                                   max=what_to_plot)
                progress_bar.update()
            else:
                progress_bar = None
            for item in self.stats_items:
                if not self.plot_what or item in self.plot_what:
                    if results_multiple:
                        plotted_files.append(self.stats_items[item].plot(plot_format=self.do_plot,
                                                                         plot_min=self.plot_min, plot_max=self.plot_max,
                                                                         aggregated=results_multiple,
                                                                         multiple_key=item))
                    else:
                        plotted_files.append(self.stats_items[item].plot(plot_format=self.do_plot,
                                                                         plot_min=self.plot_min,
                                                                         plot_max=self.plot_max))
                    if progress_bar:
                        progress_bar.next()

            if self.do_plot == PlotMethods.gretl:
                plotted_files.append(self.stats_items[list(self.stats_items.keys())[0]].plot(plot_format=self.do_plot,
                                                                                             plot_min=self.plot_min,
                                                                                             plot_max=self.plot_max,
                                                                                             generic=True))

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
        for item in self.stats_items:
            print(f"\t{item:20} {self.stats_items[item].get_description()}")

    def enable_plotting(self, plot_format: PlotMethods, plot_min: int = None, plot_max: int = None,
                        plot_what: str = ""):
        self.do_plot = plot_format
        if plot_min and plot_min >= 0:
            self.plot_min = plot_min
        if plot_max and plot_max <= self.model.config.T:
            self.plot_max = plot_max
        self.plot_what = plot_what
        if not self.export_datafile:
            self.export_datafile = "model"

    def initialize_model(self):
        if self.model.log.progress_bar and not self.do_plot and not self.export_datafile:
            # if no debug, and no output to file and no plots, then why you execute this?
            self.do_plot = PlotMethods.get_default()
            self.model.log.warning("--plot enabled due to lack of any output", before_start=True)
        if not self.model.test:
            self.model.log.step(self.current_status_save(), before_start=True)

    def finish_model(self):
        if not self.model.test:
            self.remove_not_used_data_after_abortion()
            self.determine_export_location()
            self.export_data()
            self.plot()

    def clear_output_dir(self):
        for file in [f for f in os.listdir(self.OUTPUT_DIRECTORY)]:
            if os.path.isfile(self.OUTPUT_DIRECTORY + "/" + file):
                self.model.log.info(f"Removing {self.OUTPUT_DIRECTORY + '/' + file}", before_start=True)
                os.remove(self.OUTPUT_DIRECTORY + "/" + file)

    def define_output_directory(self, output_directory):
        self.OUTPUT_DIRECTORY = output_directory

    def remove_not_used_data_after_abortion(self):
        if self.model.abort_execution:
            self.model.config.T = self.model.t
            self.dataframe = self.dataframe.head(self.model.t+1)
