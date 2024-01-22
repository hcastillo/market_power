#!/usr/bin/env python
# coding: utf-8
"""
ABM model executor, to run interactively the models
@author: hector@bith.net
"""
from market_power.model import Model
from market_power.config import Config
from util.log import Log
from util.stats_array import PlotMethods
import util.utilities as utilities
import typer
import statistics
from typing import List


# noinspection SpellCheckingInspection
def run_interactive(config: List[str] = typer.Argument(None, help="Change config value (i.e. alpha=3.1, ? to list)"),
                    log: str = typer.Option(None, help="Log level messages (? to list)"),
                    logfile: str = typer.Option(None, help="File to send the logs to"),
                    log_what: str = typer.Option(None, help="What to log (apart from balances, ? to list)"),
                    save: str = typer.Option(None, help="Save the output in csv format"),
                    readable: bool = typer.Option(False, help="Saves the output in a human readable format"),
                    plot: PlotMethods = typer.Option(None, help="Save the plot (? to list formats)"),
                    plot_tmin: int = typer.Option(None, help="Min. time to represent in the plots"),
                    plot_tmax: int = typer.Option(None, help="Max. time to represent in the plots"),
                    plot_what: str = typer.Option("", help="What to plot (all if omitted, ? to list)"),
                    clear: bool = typer.Option(False, help="Clear the output folder before execute anything"),
                    n: int = typer.Option(Config.N, help="Number of firms"),
                    t: int = typer.Option(Config.T, help="Time repetitions")):
    logger = Log(Model.default())
    models, title = utilities.manage_config_values(t, n, log, logfile, log_what, plot_tmin, plot_tmax,
                                                   plot_what, plot, logger, config)
    if clear:
        do_clear_of_output_directory()
    results = {}
    for i in range(len(models)):
        logger.set_model(models[i], plot, i, len(models) != 1)
        if readable:
            models[i].statistics.set_file_readable()
        models[i].statistics.OUTPUT_DIRECTORY = "experiment4"
        result, name_of_result = run(models[i], save)
        results[name_of_result] = result
    if len(models) > 1 and (plot or plot_what):
        models[0].statistics.plot(results)


def run_notebook():
    model = Model()
    # if we are running in a Notebook:
    model.statistics.enable_plotting(plot_format=PlotMethods.screen)
    model.statistics.interactive = False
    run(model)


def do_clear_of_output_directory():
    model = Model()
    model.statistics.clear_output_dir()


def detect_main_debt_firm(model, _data):
    bigger_l = 0
    bigger_l_firm = 0
    for firm in model.firms:
        if firm.L > bigger_l:
            bigger_l_firm = firm.id
            bigger_l = firm.L
    return dict(firm_biggerL=bigger_l_firm, biggerL=bigger_l)


def manage_stats_options(model):
    model.statistics.OUTPUT_DIRECTORY = "experiment4"
    model.export_datafile = "experiment4/model.csv"
    model.statistics.add(what="bank", name="L", prepend="bank    ")
    model.statistics.add(what="bank", name="A", prepend=" | ", logarithm=True)
    model.statistics.add(what="bank", name="D", prepend="  ")
    model.statistics.add(what="bank", name="profits", symbol="π", prepend="  ", attr_name="profits")
    model.statistics.add(what="bank", name="bad debt",
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
    model.statistics.add(what="firms", name="dK", symbol="dK", attr_name="desiredK", show=False)
    model.statistics.add(what="firms", name="offeredL", symbol="oL", show=False, function=statistics.mean)
    model.statistics.add(what="firms", name="gap_of_L", show=False)
    model.statistics.add(what="firms", name="demandL", symbol="dL", show=False, function=statistics.mean)
    model.statistics.add(what="firms", name="failures", attr_name="failed", symbol="fail",
                         number_type=int, prepend=" ")
    model.statistics.external_function_to_obtain_stats = detect_main_debt_firm


def run(model, save=None):
    manage_stats_options(model)
    return model.run(export_datafile=save)



if utilities.is_notebook():
    run_notebook()
else:
    if __name__ == "__main__":
        PlotMethods.check_sys_argv()
        typer.run(run_interactive)
