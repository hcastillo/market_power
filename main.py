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
import typer
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
    models, title = manage_config_values(t, n, log, logfile, log_what, plot_tmin, plot_tmax,
                                         plot_what, plot, logger, config)
    if clear:
        do_clear_of_output_directory()
    results = {}
    for i in range(len(models)):
        logger.set_model(models[i], plot, i, len(models) != 1)
        if readable:
            models[i].statistics.readable_file_format = True
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


def run(model, save=None):
    return model.run(export_datafile=save)


def check_what(logger, what, log_or_plot):
    result = []
    if what:
        mock_model = Model(log=logger)
        mock_model.test = True
        mock_model.initialize_model(export_datafile="mock")
        for item in what.split(","):
            if item not in mock_model.statistics.data:
                if item == '?':
                    if log_or_plot == 'plot':
                        print(logger.colors.remark(f"\t{'name':20} Σ=summation ¯=average, Ξ=logarithm scale"))
                    for valid_values in mock_model.statistics.data:
                        print(f"\t{valid_values:20} {mock_model.statistics.data[valid_values].get_description()}")
                    raise typer.Exit()
                elif item.lower() == "bank" or item.lower() == "firms":
                    logger.only_firms_or_bank = item.lower()
                else:
                    valid_values = {str(key) for key, value in mock_model.statistics.data.items()}
                    logger.error(f"{log_or_plot}_what must be one of {valid_values}", before_start=True)
                    raise typer.Exit()
            else:
                result.append(item)
    return result


def manage_plot_options(model, plot_tmin, plot_tmax, plot_what, plot, logger):
    plot_what = check_what(logger, plot_what, "plot")
    if (plot_tmin or plot_tmax or plot_what) and not plot:
        # if not enabled plot with a specific format, we assume the first type: pyplot
        plot = model.statistics.get_default_plot_method()
    if plot:
        model.statistics.enable_plotting(plot_format=plot, plot_min=plot_tmin,
                                         plot_max=plot_tmax, plot_what=plot_what)


def manage_log_options(model, log, log_what, logfile, logger):
    log_what = check_what(logger, log_what, "log")
    if log_what and not log:
        log = "INFO"
    if not log:
        log = "ERROR"
    model.log.define_log(log=log, logfile=logfile, what=log_what)


# noinspection SpellCheckingInspection
def manage_config_values(t, n, log, logfile, log_what, plot_tmin, plot_tmax, plot_what, plot, logger, config_list):
    params_only_present_once = {}
    params_present_multiple = {}
    mock_model = Model()
    if config_list:
        config_list.sort()
        for item in config_list:
            if item == '?':
                print(mock_model.config.__str__(separator="\n"))
                raise typer.Exit()
            try:
                name_config, value_config = item.split("=")
            except ValueError:
                logger.error("A config value for the model should be passed as parameter=value", before_start=True)
                raise typer.Exit(-1)
            try:
                getattr(mock_model.config, name_config)
            except AttributeError:
                logger.error(f"Configuration has no {name_config} parameter", before_start=True)
                raise typer.Exit(-1)
            try:
                setattr(mock_model.config, name_config, float(value_config))
                if name_config in params_only_present_once:
                    params_present_multiple[name_config] = [params_only_present_once[name_config], float(value_config)]
                    del params_only_present_once[name_config]
                else:
                    if name_config in params_present_multiple:
                        params_present_multiple[name_config].append(float(value_config))
                    else:
                        params_only_present_once[name_config] = float(value_config)
            except ValueError:
                logger.error(f"Value given for {value_config} is not valid", before_start=True)
                raise typer.Exit(-1)
    models = []
    num_combinations = 0
    combinations = []
    title = "" if num_combinations == 1 else f"{params_present_multiple}"
    for item in cartesian_product(params_present_multiple):
        combinations.append(item)
        num_combinations += 1
    for i in range(num_combinations):
        one_combination_of_multiple_params = combinations[i]
        if num_combinations > 1:
            model = Model(model_id=f"{i}", model_title=f"{one_combination_of_multiple_params}", log=logger)
        else:
            model = Model()
        if t != model.config.T:
            model.config.T = t
        if n != model.config.N:
            model.config.N = n
        manage_log_options(model, log, log_what, logfile, logger)
        manage_plot_options(model, plot_tmin, plot_tmax, plot_what, plot, logger)
        for param in params_only_present_once:
            setattr(model.config, param, params_only_present_once[param])
        for param in one_combination_of_multiple_params:
            setattr(model.config, param, one_combination_of_multiple_params[param])
        models.append(model)
    return models, title


def cartesian_product(my_dictionary):
    from itertools import product
    return (dict(zip(my_dictionary.keys(), values)) for values in product(*my_dictionary.values()))


def is_notebook():
    try:
        __IPYTHON__
        return get_ipython().__class__.__name__ != "SpyderShell"
    except NameError:
        return False


if is_notebook():
    run_notebook()
else:
    if __name__ == "__main__":
        PlotMethods.check_sys_argv()
        typer.run(run_interactive)
