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

    @staticmethod
    def get_plot_formats():
        return ["pyplot", "bokeh", "grace", "gretl"]

    def get_description(self):
        return f"{self.repr_function if self.repr_function else ' '} {self.attr_name:10}"

    def plot(self, plot_format: str, plot_min: int = None, plot_max: int = None, multiple=None, multiple_key=None):
        if not plot_min or plot_min < 0:
            plot_min = 0
        if not plot_max or plot_max > self.model.config.T:
            plot_max = self.model.config.T
        if self.do_plot:
            y_label = self.repr_function + self.description + "(ln)" if self.logarithm else ""
            if multiple:
                filename = self.model.statistics.OUTPUT_DIRECTORY + "/" + self.filename()
                title = self.its_name + " " + self.repr_function + self.description
                plot_format = "pyplot"
            else:
                filename = self.model.statistics.OUTPUT_DIRECTORY + "/" + \
                           self.model.get_id_for_filename() + self.filename()
                title = self.its_name + " " + self.repr_function + self.description + self.model.model_title
            match plot_format:
                case "bokeh" | "screen":
                    import bokeh.plotting
                    xx = []
                    yy = []
                    for i in range(plot_min, plot_max):
                        if not np.isnan(self.data[i]):
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

                case "grace":
                    from pygrace.project import Project
                    plot = Project()
                    graph = plot.add_graph()
                    graph.title.text = title.encode('ascii', 'replace').decode()
                    data = []
                    for i in range(plot_min, plot_max):
                        if not np.isnan(self.data[i]):
                            data.append((i, self.data[i]))
                    graph.add_dataset(data)
                    graph.autoscalex()
                    graph.autoscaley()
                    graph.autoticky()
                    plot.saveall(filename + ".agr")
                    return filename + ".agr"

                case "gretl":
                    if not self.model.export_datafile:
                        exported_data = self.model.statistics.get_export_path("exported.txt")
                        import os
                        if not os.path.isfile(exported_data):
                            self.model.statistics.export_data(export_datafile=exported_data)
                    else:
                        exported_data = self.model.export_datafile
                    with open(filename + ".inp", 'w', encoding="utf-8") as script:
                        script.write(f"open {exported_data}\n")
                        script.write("setobs 1 1 --special-time-series\n")
                        script.write(f"gnuplot {self.its_name}{self.short_description.upper()}" +
                                     f" --time-series --with-lines\n")
                        script.write(f"quit()\n")
                    return filename + ".inp"

                case _:
                    import matplotlib.pyplot as plt
                    plt.clf()
                    if multiple:
                        for element in multiple:
                            xx, yy = StatsArray.get_plot_elements(multiple[element][multiple_key].data,
                                                                  plot_min, plot_max)
                            plt.plot(xx, yy, label=element)
                        plt.legend()
                    else:
                        xx, yy = StatsArray.get_plot_elements(self.data, plot_min, plot_max)
                        plt.plot(xx, yy)
                        plt.ylabel(y_label)
                    plt.xticks(xx)
                    plt.xlabel("t")
                    plt.title(title)
                    plt.savefig(filename + ".png")
                    # plt.show()
                    return filename + ".png"

        return None

    @staticmethod
    def get_plot_elements(the_array, plot_min, plot_max):
        xx = []
        yy = []
        for i in range(plot_min, plot_max):
            if not np.isnan(the_array[i]):
                xx.append(i)
                yy.append(the_array[i])
        return xx, yy

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
