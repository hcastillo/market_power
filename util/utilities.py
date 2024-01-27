#!/usr/bin/env python
# coding: utf-8
"""
ABM model: Non core functions used in some parts of the code

@author: hector@bith.net
"""
from market_power.model import Model
import os

def cartesian_product(my_dictionary):
    """
    :param my_dictionary: {'a':[1,2,3],'b':[4,5,6]}
    :return:  iterative list of combinations as dictionary: {'a': 1, 'b': 4} {'a': 1, 'b': 5}...
    """
    from itertools import product
    return (dict(zip(my_dictionary.keys(), values)) for values in product(*my_dictionary.values()))


def is_notebook():
    try:
        # noinspection PyStatementEffect
        __IPYTHON__
        return get_ipython().__class__.__name__ != "SpyderShell"
    except NameError:
        return False


def check_what(logger, what, log_or_plot):
    result = []
    if what:
        mock_model = Model(log=logger)
        mock_model.test = True
        mock_model.initialize_model(export_datafile="mock")
        for item in what.split(","):
            if item not in mock_model.statistics.stats_items:
                if item == '?':
                    if log_or_plot == 'plot':
                        print(logger.colors.remark(f"\t{'name':20} Σ=summation ¯=average, Ξ=logarithm scale"))
                    for valid_values in mock_model.statistics.stats_items:
                        print(f"\t{valid_values:20} {mock_model.statistics.stats_items[valid_values].get_description()}")
                    raise typer.Exit()
                elif item.lower() == "bank" or item.lower() == "firms":
                    logger.only_firms_or_bank = item.lower()
                else:
                    valid_values = {str(key) for key, value in mock_model.statistics.stats_items.items()}
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


def manage_directory(model, directory, clear):
    if not os.path.exists(directory):
        os.mkdir(directory)
    model.statistics.OUTPUT_DIRECTORY = directory
    if clear:
        model.statistics.clear_output_dir()


# noinspection SpellCheckingInspection
def manage_config_values(t, n, log, logfile, log_what, plot_tmin, plot_tmax, plot_what, plot, logger,
                         config_list, directory, clear):
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
        manage_directory(model, directory, clear)
        manage_log_options(model, log, log_what, logfile, logger)
        manage_plot_options(model, plot_tmin, plot_tmax, plot_what, plot, logger)
        for param in params_only_present_once:
            setattr(model.config, param, params_only_present_once[param])
        for param in one_combination_of_multiple_params:
            setattr(model.config, param, one_combination_of_multiple_params[param])
        models.append(model)
    return models, title
