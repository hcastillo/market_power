#!/usr/bin/env python
# coding: utf-8
"""
ABM model auxiliary file: logging facilities
@author: hector@bith.net
"""
import numpy as np
import math


class StatsArray:
    def __init__(self, its_model, data_type, description,
                 short_description, prepend="", plot=True, attr_name=None, logarithm=False):
        self.description = description
        self.short_description = short_description
        self.model = its_model
        self.prepend = prepend
        self.its_name = ""
        self.repr_function = ""
        self.logarithm = logarithm
        if attr_name:
            self.attr_name = attr_name
        else:
            self.attr_name = self.short_description
        self.data = np.zeros(its_model.config.T, dtype=data_type)
        self.do_plot = plot

    @staticmethod
    def get_value(element):
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

    @staticmethod
    def get_plot_formats():
        return ["pyplot", "bokeh", "pygrace"]

    def get_description(self):
        return f"{self.repr_function if self.repr_function else ' '} {self.attr_name:10}"

    def plot(self, plot_format: str, plot_min: int=None, plot_max: int=None):
        if not plot_min or plot_min<0:
            plot_min = 0
        if not plot_max or plot_max > self.model.config.T:
            plot_max = self.model.config.T
        if self.do_plot:
            title = self.its_name + " " + self.repr_function + self.description
            y_label = self.repr_function + self.description + "(ln)" if self.logarithm else ""
            filename = self.model.statistics.OUTPUT_DIRECTORY + "/" + self.filename()

            match plot_format:
                case "bokeh" | "screen":
                    import bokeh.plotting
                    xx = []
                    yy = []
                    for i in range(plot_min, plot_max):
                        xx.append(i)
                        yy.append(self.data[i])
                    p = bokeh.plotting.figure(title=title, x_axis_label="t", y_axis_label=y_label,
                                              sizing_mode="stretch_width", height=550)
                    p.line(xx, yy, color="blue", line_width=2)
                    if plot_format == "screen":
                        bokeh.plotting.output_notebook()
                        bokeh.plotting.show(p)
                    else:
                        bokeh.plotting.output_file(filename + ".html", title=title)
                        bokeh.plotting.save(p)
                        return filename + ".html"

                case "pygrace":
                    from pygrace.project import Project
                    import unicodedata
                    plot = Project()
                    graph = plot.add_graph()
                    graph.title.text = title.encode('ascii', 'replace').decode()
                    data = []
                    for i in range(plot_min, plot_max):
                        data.append([i, self.data[i]])
                    graph.add_dataset(data)
                    graph.autoscalex()
                    graph.autotickx()
                    _x_min, _y_min, _x_max, _y_max = graph.get_world()
                    graph.set_world(_x_min, _x_min, _x_max, _x_max)
                    graph.autoticky()
                    graph.remove_extraworld_drawing_objects()
                    plot.saveall(filename + ".agr")
                    return filename + ".agr"

                case _:
                    import matplotlib.pyplot as plt
                    plt.clf()
                    xx = []
                    yy = []
                    for i in range(plot_min, plot_max):
                        xx.append(i)
                        yy.append(self.data[i])
                    plt.plot(xx, yy, 'b-')
                    plt.ylabel(y_label)
                    plt.xlabel("t")
                    plt.title(title)
                    plt.savefig(filename + ".png")
                    # plt.show()
                    return filename + ".png"
        return None

    def __str__(self):
        if self.its_name != "":
            return self.its_name + self.short_description.upper()
        else:
            return self.short_description.upper()

    def filename(self):
        return self.its_name.lower() + "_" + self.description.lower().replace(" ", "_")


class StatsFirms(StatsArray):
    def __init__(self, its_model, data_type, description, short_description,
                 prepend="", plot=True, attr_name=None, function=sum, repr_function="Σ", logarithm=False):
        super().__init__(its_model, data_type, description, short_description, prepend, plot, attr_name, logarithm)
        self.function = function
        self.its_name = "Firms"
        self.repr_function = repr_function

    def store_statistics(self):
        result = self.function(self.get_value(getattr(firm, self.attr_name)) for firm in self.model.firms)
        self.data[self.model.t] = math.log(result) if self.logarithm else result
        return self.prepend + self.repr_function + self.__return_value_formatted__()


class StatsBankSector(StatsArray):
    def __init__(self, its_model, data_type, description, short_description,
                 prepend="", plot=True, attr_name=None, logarithm=False):
        super().__init__(its_model, data_type, description, short_description, prepend, plot, attr_name, logarithm)
        self.function = None
        self.its_name = "Bank"
        self.repr_function = ""

    def store_statistics(self):
        result = getattr(self.model.bank_sector, self.attr_name)
        self.data[self.model.t] = math.log(result) if self.logarithm else result
        return self.prepend + self.__return_value_formatted__()
