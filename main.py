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
from util.utilities import is_notebook, manage_config_values
import typer
import statistics
from typing import List


# noinspection SpellCheckingInspection
def run_interactive(config: List[str] = typer.Argument(None, help="Change config value (i.e. alpha=3.1, ? to list)"),
                    log: str = typer.Option(None, help="Log level messages (? to list)"),
                    logfile: str = typer.Option(None, help="File to send the logs to"),
                    log_what: str = typer.Option(None, help="What to log (apart from balances, ? to list)"),
                    save: str = typer.Option(None, help="Save the output in csv format"),
                    directory: str = typer.Option(Model.default().statistics.OUTPUT_DIRECTORY,
                                                  help="Directory where it stores the output"),
                    readable: bool = typer.Option(False, help="Saves the output in a human readable format"),
                    plot: PlotMethods = typer.Option(None, help="Save the plot (? to list formats)"),
                    plot_tmin: int = typer.Option(None, help="Min. time to represent in the plots"),
                    plot_tmax: int = typer.Option(None, help="Max. time to represent in the plots"),
                    plot_what: str = typer.Option("", help="What to plot (all if omitted, ? to list)"),
                    clear: bool = typer.Option(False, help="Clear the output folder before execute anything"),
                    n: int = typer.Option(Config.N, help="Number of firms"),
                    t: int = typer.Option(Config.T, help="Time repetitions")):
    logger = Log(Model.default())
    models, title = manage_config_values(t, n, log, logfile, log_what, plot_tmin, plot_tmax,
                                         plot_what, plot, logger, config, directory, clear)
    results = {}
    for i in range(len(models)):
        logger.set_model(models[i], plot, i, len(models))
        if readable:
            models[i].statistics.set_file_readable()
        result, name_of_result = run(models[i], save)
        results[name_of_result] = result
    plot_aggregated_plots_and_description(models, results, plot, plot_what, logger)


def plot_aggregated_plots_and_description(models, results, plot, plot_what, logger):
    if len(models) > 1:
        if plot or plot_what:
            # plot the aggregated plots:
            models[0].statistics.plot(results)
        filename_for_description = models[0].statistics.OUTPUT_DIRECTORY + "/" + \
                                   models[0].export_datafile.replace(models[0].get_id_for_export(),"") + ".info"
        with open(filename_for_description, 'w', encoding="utf-8") as file_for_description:
            results_description = list(results.keys())
            for i in range(len(models)):
                file_for_description.write(f"{models[i].export_datafile}" +
                                           f"{models[i].statistics.export_datafile_extension}: " +
                                           f"{results_description[i]}\n")
        logger.progress_bar_multiple.next()


def run_notebook():
    global model
    model = Model()
    # if we are running in a Notebook:
    model.statistics.enable_plotting(plot_format=PlotMethods.screen)
    model.statistics.interactive = False
    run(model)





# def special_stats_function(model,data):
#     """
#     function called each time at the end of each step, before clearing the bankrupted firms
#     not used in this code (to use it, uncomment the reference upper, as model.statistics.function = special...
#     :param model: Model object
#     :param data: direct reference to model.statistics.data
#     :return:
#     """
#     avg_A = data['firms_A'][model.t]
#     for firm in model.firms:
#         if firm.A < 0 and avg_A<abs(firm.A):
#             print(model.t,firm,firm.A,firm.gamma,model.bank_sector.bad_debt,firm.Y,firm.u,firm.Aprev)


def manage_stats_options(model):
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
    model.statistics.add(what="firms", name="desiredK", symbol="dK", show=False)
    model.statistics.add(what="firms", name="offeredL", symbol="oL", show=False, function=statistics.mean)
    model.statistics.add(what="firms", name="gap_of_L", show=False)
    model.statistics.add(what="firms", name="demandL", symbol="dL", show=False, function=statistics.mean)
    model.statistics.add(what="firms", name="failures", attr_name="failed", symbol="fail",
                         number_type=int, prepend=" ")
    # model.statistics.external_function_to_obtain_stats = special_stats_function


def run(model, save=None):
    manage_stats_options(model)
    return model.run(export_datafile=save)


if is_notebook():
    run_notebook()
else:
    if __name__ == "__main__":
        PlotMethods.check_sys_argv()
        typer.run(run_interactive)
