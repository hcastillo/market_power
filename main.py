#!/usr/bin/env python
# coding: utf-8
"""
ABM model executer, to run interactively the modelss
@author: hector@bith.net
"""
from market_power.model import Model
from market_power.config import Config
from util.log import Log
import typer
from typing import List


def run_interactive(config: List[str] = typer.Argument(None, help="Change config value (i.e. alpha=3.1, ? to list)"),
                    log: str = typer.Option(None, help="Log level messages (ERROR,WARNING,INFO,DEBUG)"),
                    logfile: str = typer.Option(None, help="File to send the logs to"),
                    log_what: str = typer.Option(None, help="What to log (apart from balances, ? to list)"),
                    save: str = typer.Option(None, help="Save the output of this execution"),
                    plot: str = typer.Option(None, help="Save the plot (? to list formats)"),
                    plot_tmin: int = typer.Option(None, help="Min. time to represent in the plots"),
                    plot_tmax: int = typer.Option(None, help="Max. time to represent in the plots"),
                    plot_what: str = typer.Option("", help="What to plot (all if omitted, ? to list)"),
                    clear: bool = typer.Option(False, help="Clear the output folder before execute anything"),
                    n: int = typer.Option(Config.N, help="Number of firms"),
                    t: int = typer.Option(Config.T, help="Time repetitions")):
    logger = Log()
    models, title = manage_config_values(t, n, log, logfile, log_what, plot_tmin, plot_tmax,
                                         plot_what, plot, logger, config)
    if clear:
        do_clear_of_output_directory()
    results = []
    for i in range(len(models)):
        logger.set_model(models[i])
        results.append(run(models[i], save))
    if len(models) > 1 and plot:
        plot_multiple(results, plot_tmin, plot_tmax, plot)


def run_notebook():
    model = Model()
    # if we are running in a Notebook:
    model.statistics.enable_plotting(plot_format="screen")
    model.statistics.interactive = False
    run(model)


def do_clear_of_output_directory():
    model = Model()
    model.statistics.clear_output_dir()


def run(model, save=None):
    return model.run(export_datafile=save)


def plot_multiple(results, plot_min, plot_max, plot):
    for i in results[0]:
        results[0][i].plot(plot, plot_min, plot_max, results, i)


def list_what():
    mock_model = Model()
    mock_model.initialize_model(export_datafile="mock")
    mock_model.statistics.get_what()
    raise typer.Exit()


def manage_plot_options(model, plot_tmin, plot_tmax, plot_what, plot):
    if plot_what == '?':
        list_what()
    else:
        if (plot_tmin or plot_tmax or plot_what) and not plot:
            # if not enabled plot with a specific format, we assume the first type: pyplot
            plot = model.statistics.get_plot_formats()[0]
        if plot:
            if plot == '?':
                model.statistics.get_plot_formats(display=True)
                raise typer.Exit()
            else:
                if plot.lower() in model.statistics.get_plot_formats():
                    model.statistics.enable_plotting(plot_format=plot.lower(), plot_min=plot_tmin,
                                                     plot_max=plot_tmax, plot_what=plot_what)
                else:
                    model.log.error(f"Plot format must be one of {model.statistics.get_plot_formats()}",
                                    before_start=True)
                    raise typer.Exit(-1)


def manage_log_options(model, log, log_what, logfile):
    if log_what and not log:
        log = "INFO"
    if not log:
        log = "ERROR"
    if log_what == '?':
        list_what()
    else:
        model.log.define_log(log=log, logfile=logfile, what=log_what)


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
        manage_log_options(model, log, log_what, logfile)
        manage_plot_options(model, plot_tmin, plot_tmax, plot_what, plot)
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
        typer.run(run_interactive)
