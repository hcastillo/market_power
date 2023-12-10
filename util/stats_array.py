#!/usr/bin/env python
# coding: utf-8
"""
ABM model auxiliary file: logging facilities
@author: hector@bith.net
"""
import numpy as np
import math
from enum import Enum


# noinspection SpellCheckingInspection
class PlotMethods(str, Enum):
    pyplot = "pyplot"
    bokeh = "bokeh"
    grace = "grace"
    gretl = "gretl"
    screen = "screen"

    @classmethod
    def _missing_(cls, _):
        return cls.pyplot

    def plot(self, plot_min, plot_max, filename, title, y_label, series_name,
             data, model, multiple=None, multiple_key=None):
        match self.name:
            case PlotMethods.bokeh | PlotMethods.screen:
                import bokeh.plotting
                from bokeh.palettes import Category20
                p = bokeh.plotting.figure(title=title, x_axis_label="t", y_axis_label=y_label,
                                          sizing_mode="stretch_width", height=550)
                if not multiple:
                    xx, yy = StatsArray.get_plot_elements(data, plot_min, plot_max)
                    p.line(xx, yy, color="blue", line_width=2)
                else:
                    i = 0
                    for element in multiple:
                        xx, yy = StatsArray.get_plot_elements(multiple[element][multiple_key].data,
                                                              plot_min, plot_max)
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

                if multiple:
                    plot = Project(colors=ColorBrewerScheme('Paired'))
                else:
                    plot = Project()

                graph = plot.add_graph()
                graph.title.text = title.encode('ascii', 'replace').decode()
                if multiple:
                    i = 0
                    datasets = []
                    for element in multiple:
                        datasets.append(
                            graph.add_dataset(StatsArray.get_plot_elements(multiple[element][multiple_key].data,
                                                                           plot_min, plot_max, two_list=False),
                                              legend=element))
                        datasets[-1].symbol.fill_color = i
                        i += 1
                else:
                    graph.add_dataset(StatsArray.get_plot_elements(data, plot_min, plot_max, two_list=False))
                    graph.yaxis.label.text = 'y_label'
                graph.autoscalex()
                graph.autoscaley()
                graph.autoticky()
                graph.xaxis.label.text = 't'
                plot.saveall(filename + ".agr")
                return filename + ".agr"

            case PlotMethods.gretl:
                with open(filename + ".inp", 'w', encoding="utf-8") as script:
                    import os
                    script.write(f"set workdir " + os.getcwd() + "\n")
                    script.write(f"open {model.export_datafile}\n")
                    script.write("setobs 1 1 --special-time-series\n")
                    if multiple:
                        series_to_plot = f" {series_name}_0"
                        for i in range(1, len(multiple)):
                            another_model_filename = model.export_datafile.replace("_0.txt", f"_{i}.txt")
                            script.write(f"append {another_model_filename}\n")
                            series_to_plot += f" {series_name}_{i}"
                        script.write(f"gnuplot {series_to_plot} --time-series --with-lines\n")
                    else:
                        if model.get_id_for_filename() != '':
                            series_name += "_" + model.get_id_for_filename().replace("_", "")
                        script.write(f"gnuplot {series_name} --time-series --with-lines\n")
                    script.write(f"exit()\n")
                return filename + ".inp"

            case _:
                import matplotlib.pyplot as plt
                plt.clf()
                xx = []
                if multiple:
                    for element in multiple:
                        xx, yy = StatsArray.get_plot_elements(multiple[element][multiple_key].data,
                                                              plot_min, plot_max)
                        plt.plot(xx, yy, label=element)
                    plt.legend()
                else:
                    xx, yy = StatsArray.get_plot_elements(data, plot_min, plot_max)
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
            if sys.argv[i] == "--plot" and sys.argv[i + 1].startswith("-"):
                sys.argv.insert(i + 1, PlotMethods('default').name)
        if sys.argv[-1] == '--plot':
            sys.argv.append(PlotMethods('default').name)


class StatsArray:
    def __init__(self, its_model, data_type, description,
                 short_description, prepend="", plot=True, attr_name=None, logarithm=False, show=True):
        self.description = description
        self.short_description = short_description
        self.model = its_model
        self.prepend = prepend
        self.its_name = ""
        self.repr_function = ""
        self.show = show
        self.logarithm = logarithm
        if attr_name:
            self.attr_name = attr_name
        else:
            self.attr_name = self.short_description
        self.data = np.zeros(its_model.config.T, dtype=data_type)
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
        result += f"{self.model.log.format(self.data[self.model.t])}"
        return result

    def __getitem__(self, t):
        return self.model.log.format(self.data[t])

    def __get__(self):
        return self.data

    def get_description(self):
        return f"{self.repr_function if self.repr_function else ' '} {self.attr_name:10}"

    def plot(self, plot_format: PlotMethods, plot_min: int = None, plot_max: int = None, multiple=None,
             multiple_key=None):
        if not plot_min or plot_min < 0:
            plot_min = 0
        if not plot_max or plot_max > self.model.config.T:
            plot_max = self.model.config.T
        if self.do_plot:
            y_label = self.repr_function + self.description + "(ln)" if self.logarithm else ""
            series_name = f"{self.its_name}{self.short_description.upper()}"
            if multiple:
                filename = self.model.statistics.OUTPUT_DIRECTORY + "/" + self.filename()
                title = self.its_name + " " + self.repr_function + self.description
            else:
                filename = self.model.statistics.OUTPUT_DIRECTORY + "/" + \
                           self.model.get_id_for_filename() + self.filename()
                title = self.its_name + " " + self.repr_function + self.description + self.model.model_title

            return plot_format.plot(plot_min, plot_max, filename, title, y_label, series_name, self.data,
                                    self.model, multiple, multiple_key)
        return None

    @staticmethod
    def get_plot_elements(the_array, plot_min, plot_max, two_list=True):
        xx = []
        yy = []
        for i in range(plot_min, plot_max):
            if not np.isnan(the_array[i]):
                if two_list:
                    xx.append(i)
                    yy.append(the_array[i])
                else:
                    xx.append((i, the_array[i]))
        if two_list:
            return xx, yy
        else:
            return xx

    def __str__(self):
        if self.its_name != "":
            return self.its_name + self.short_description.upper()
        else:
            return self.short_description.upper()

    def filename(self):
        return self.its_name.lower() + "_" + self.description.lower().replace(" ", "_")


class StatsFirms(StatsArray):
    def __init__(self, its_model, data_type, description, short_description,
                 prepend="", plot=True, attr_name=None, function=sum, repr_function="Σ", logarithm=False, show=True):
        super().__init__(its_model, data_type, description, short_description,
                         prepend, plot, attr_name, logarithm, show)
        self.function = function
        self.its_name = "Firms"
        self.repr_function = repr_function

    def store_statistics(self):
        result = self.function(self.get_value(firm) for firm in self.model.firms)
        self.data[self.model.t] = math.log(result) if self.logarithm else result
        if self.show:
            return self.prepend + self.repr_function + self.__return_value_formatted__()
        else:
            return ""


class StatsBankSector(StatsArray):
    def __init__(self, its_model, data_type, description, short_description,
                 prepend="", plot=True, attr_name=None, logarithm=False, show=True):
        super().__init__(its_model, data_type, description, short_description,
                         prepend, plot, attr_name, logarithm, show)
        self.function = None
        self.its_name = "Bank"
        self.repr_function = ""

    def store_statistics(self):
        result = getattr(self.model.bank_sector, self.attr_name)
        self.data[self.model.t] = math.log(result) if self.logarithm else result
        if self.show:
            return self.prepend + self.__return_value_formatted__()
        else:
            return ""
