#!/usr/bin/env python
# coding: utf-8
"""
ABM model auxiliary file: logging facilities
@author: hector@bith.net
"""
import numpy as np
import math
import os
from enum import Enum


# noinspection SpellCheckingInspection
class PlotMethods(str, Enum):
    pyplot = "pyplot"
    bokeh = "bokeh"
    grace = "grace"
    gretl = "gretl"
    screen = "screen"

    # @classmethod
    #def _missing_(cls, _):
    #    return cls.pyplot

    @staticmethod
    def get_default():
        return PlotMethods('pyplot')

    def __str__(self):
        return self.value

    def plot(self, plot_min, plot_max, filename, title, y_label, series_name,
             data, model, aggregated=None, multiple_key=None, logarithm=False):
        match self.name:
            case PlotMethods.bokeh | PlotMethods.screen:
                import bokeh.plotting
                from bokeh.palettes import Category20
                p = bokeh.plotting.figure(title=title, x_axis_label="t", y_axis_label=y_label,
                                          sizing_mode="stretch_width", height=550)
                if not aggregated:
                    xx, yy = StatsBaseClass.get_plot_elements(data, plot_min, plot_max, logarithm)
                    p.line(xx, yy, color="blue", line_width=2)
                else:
                    i = 0
                    for element in aggregated:
                        xx, yy = StatsBaseClass.get_plot_elements(aggregated[element][multiple_key].stats_items,
                                                                  plot_min, plot_max, logarithm)
                        p.line(xx, yy, color=Category20[20][i % 20], line_width=2, legend_label=element)
                        i += 1
                if self.name == PlotMethods.screen:
                    bokeh.plotting.output_notebook()
                    bokeh.plotting.show(p)
                else:
                    bokeh.plotting.output_file(filename + ".html", title=title)
                    bokeh.plotting.save(p)
                    return filename + ".html"

            case PlotMethods.grace:
                from pygrace.project import Project
                from pygrace.colors import ColorBrewerScheme

                if aggregated:
                    plot = Project(colors=ColorBrewerScheme('Paired'))
                else:
                    plot = Project()

                graph = plot.add_graph()
                graph.title.text = title.encode('ascii', 'replace').decode()
                if aggregated:
                    i = 0
                    datasets = []
                    for element in aggregated:
                        datasets.append(
                            graph.add_dataset(StatsBaseClass.get_plot_elements(
                                aggregated[element][multiple_key].stats_items,
                                plot_min, plot_max, logarithm, two_list=False),
                            legend=element))
                        datasets[-1].symbol.fill_color = i
                        i += 1
                else:
                    graph.add_dataset(StatsBaseClass.get_plot_elements(data, plot_min,
                                                                       plot_max, logarithm, two_list=False))
                    graph.yaxis.label.text = 'y_label'
                graph.autoscalex()
                graph.autoscaley()
                graph.autoticky()
                graph.xaxis.label.text = 't'
                plot.saveall(filename + ".agr")
                return filename + ".agr"

            case PlotMethods.gretl:
                with open(filename + ".inp", 'w', encoding="utf-8") as script:
                    script.write(f"open {model.export_datafile}{model.statistics.export_datafile_extension}\n")
                    script.write("setobs 1 1 --special-time-series\n")
                    if title is not None:
                        if aggregated:
                            series_to_plot = f" {series_name}_0"
                            for i in range(1, len(aggregated)):
                                another_model_filename = model.export_datafile.replace("_0", f"_{i}") + \
                                                         model.statistics.export_datafile_extension
                                script.write(f"append {another_model_filename}\n")
                                series_to_plot += f" {series_name}_{i}"
                            script.write(f"gnuplot {series_to_plot} --time-series --with-lines --output=display\n")
                        else:
                            if model.get_id_for_export() != '':
                                series_name += "_" + model.get_id_for_export().replace("_", "")
                            script.write(f"gnuplot {series_name} --time-series --with-lines --output=display\n")
                        script.write(f"exit()\n")
                return filename + ".inp"

            case _:
                import matplotlib.pyplot as plt
                plt.clf()
                xx = []
                if aggregated:
                    for element in aggregated:
                        xx, yy = StatsBaseClass.get_plot_elements(aggregated[element][multiple_key],
                                                                  plot_min, plot_max, logarithm)
                        plt.plot(xx, yy, label=element)
                    plt.legend()
                else:
                    xx, yy = StatsBaseClass.get_plot_elements(data, plot_min, plot_max, logarithm)
                    plt.plot(xx, yy)
                    plt.ylabel(y_label)
                plt.xticks(xx)
                plt.xlabel("t")
                plt.title(title)
                plt.savefig(filename + ".png")
                # plt.show()
                return filename + ".png"

    @staticmethod
    def check_sys_argv():
        import sys
        for i in range(len(sys.argv) - 1):
            if sys.argv[i] == "--plot":
                if sys.argv[i + 1].startswith("-"):
                    sys.argv.insert(i + 1, PlotMethods.get_default().name)
                if sys.argv[i + 1] == '?':
                    for item in [e.value for e in PlotMethods]:
                        print(f"\t{item}")
                    sys.exit(0)
        if sys.argv[-1] == '--plot':
            sys.argv.append(PlotMethods.get_default().name)


class StatsBaseClass:
    def __init__(self, its_model, description,
                 short_description, column_name, prepend="", number_type=float,
                 plot=True, attr_name=None, logarithm=False, show=True):
        self.description = description
        self.short_description = short_description
        self.model = its_model
        self.prepend = prepend
        self.its_name = ""
        self.function = None
        self.column_name = column_name
        self.repr_function = ""
        self.show = show
        self.logarithm = logarithm
        if attr_name:
            self.attr_name = attr_name
        else:
            self.attr_name = self.short_description
        if self.column_name not in its_model.statistics.dataframe.keys():
            its_model.statistics.dataframe.insert(len(its_model.statistics.dataframe.keys()),
                                                  self.column_name, 0.0 if number_type == float else 0, True)
        self.do_plot = plot

    def get_value(self, firm):
        element = getattr(firm, self.attr_name)
        if callable(element):
            return element()
        else:
            return element

    def __return_value_formatted__(self):
        result = f"{self.short_description}"
        result += "Ξ" if self.logarithm else "="
        value = self.model.statistics.dataframe[self.column_name][self.model.t]
        if self.logarithm:
            value = math.log(value) if value>0 else math.nan
        result += f"{self.model.log.format(value)}"
        return result

    def __getitem__(self, t):
        return self.model.log.format(self.model.statistics.dataframe[self.column_name][t])

    def __get__(self):
        return self.model.statistics.dataframe[self.column_name]

    def get_description(self):
        return f"{self.repr_function if self.repr_function else ' '} {self.attr_name:10}"

    def plot(self, plot_format: PlotMethods, plot_min: int = None, plot_max: int = None, aggregated=None,
             multiple_key=None, generic=False):
        if not plot_min or plot_min < 0:
            plot_min = 0
        if not plot_max or plot_max > self.model.config.T:
            plot_max = self.model.config.T
        if self.do_plot:
            filename = self.model.statistics.OUTPUT_DIRECTORY+"/"+self.model.export_datafile
            if generic:
                y_label = ""
                series_name = ""
                title = None
            else:
                y_label = self.repr_function + self.description + "(ln)" if self.logarithm else ""
                series_name = f"{self.name_for_files()}"
                filename += "_" + self.filename()
                title = self.its_name + " " + self.repr_function + self.description + self.model.model_title
            if aggregated:
                # aggregated is a combined plot of multiple models, i.e.: eta=0.1 eta=0.2, it will generate a
                # plot as model_firms_a with the results of BOTH models for A, another file for L, etc:
                filename = filename.replace(self.model.get_id_for_export(), "")
                title = self.its_name + " " + self.repr_function + self.description
            return plot_format.plot(plot_min, plot_max, filename, title, y_label, series_name,
                                    self.model.statistics.dataframe[self.column_name],
                                    self.model, aggregated, multiple_key, self.logarithm)
        return None

    @staticmethod
    def get_plot_elements(the_array, plot_min, plot_max, logarithm, two_list=True):
        xx = []
        yy = []
        for i in range(plot_min, plot_max):
            if not np.isnan(the_array[i]):
                if two_list:
                    xx.append(i)
                    yy.append(StatsBaseClass.get_the_item(the_array, i, logarithm))
                else:
                    xx.append((i, StatsBaseClass.get_the_item(the_array, i, logarithm)))
        if two_list:
            return xx, yy
        else:
            return xx

    @staticmethod
    def get_the_item(the_array, position, logarithm):
        value = the_array[position]
        if logarithm:
            return math.log(value) if value > 0 else math.nan
        else:
            return value

    def __str__(self):
        if self.its_name != "":
            return self.its_name + self.short_description.upper()
        else:
            return self.short_description.upper()

    def name_for_files(self):
        text = self.short_description if self.short_description.isascii() else self.description
        if self.its_name != "":
            return self.its_name + text.upper().replace(" ", "")
        else:
            return text.upper().replace(" ", "")

    def filename(self):
        return self.its_name.lower() + "_" + self.description.lower().replace(" ", "_")

    def get_statistics(self, store=True):
        value = self._calculate_statistics()
        if store:
            if self.model.t >= len(self.model.statistics.dataframe):
                self.model.statistics.dataframe.loc[self.model.t] = 0.0
            self.model.statistics.dataframe[self.column_name][self.model.t] = value
        if self.show:
            return self.prepend + self.repr_function + self.__return_value_formatted__()
        else:
            return ""


class StatsFirms(StatsBaseClass):
    def __init__(self, its_model, description, short_description, column_name,
                 prepend="", number_type=float, plot=True, attr_name=None, function=sum,
                 repr_function="Σ", logarithm=False, show=True):
        super().__init__(its_model, description, short_description, column_name,
                         prepend, number_type, plot, attr_name, logarithm, show)
        self.function = function
        self.repr_function = repr_function
        self.its_name = "Firms"

    def _calculate_statistics(self):
        return self.function(self.get_value(firm) for firm in self.model.firms)


class StatsBankSector(StatsBaseClass):
    def __init__(self, its_model, description, short_description, column_name,
                 prepend="", number_type=float, plot=True, attr_name=None, logarithm=False, show=True):
        super().__init__(its_model, description, short_description, column_name,
                         prepend, number_type, plot, attr_name, logarithm, show)
        self.its_name = "Bank"

    def _calculate_statistics(self):
        return getattr(self.model.bank_sector, self.attr_name)


class StatsSpecificFirm(StatsBaseClass):
    def __init__(self, its_model, description, short_description, column_name, firm_number,
                 prepend="", number_type=float, plot=True, attr_name=None, logarithm=False, show=False):
        super().__init__(its_model, description, short_description, column_name,
                         prepend, number_type, plot, attr_name, logarithm, show)
        self.firm_number = firm_number
        self.its_name = f"Firm{firm_number}_"

    def _calculate_statistics(self):
        return self.get_value(self.model.firms[self.firm_number])


class StatsSpecificData(StatsBaseClass):
    def __init__(self, its_model, description,
                 number_type=float, plot=True, attr_name=None, logarithm=False, show=False):
        super().__init__(its_model, description, description, description,
                         "", number_type, plot, attr_name, logarithm, show)

    def _calculate_statistics(self):
        pass