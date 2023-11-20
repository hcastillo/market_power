#!/usr/bin/env python
# coding: utf-8
"""
ABM model executer, to run interactively the model
@author: hector@bith.net
"""
from market_power.model import Model
from market_power.config import Config
import typer
from typing import List


def run_interactive(getconfig: bool = typer.Option(False, help="Get current configuration"),
                    setconfig: List[str] = typer.Argument(None, help="Change config value (i.e. alpha=3.1"),
                    log: str = typer.Option('WARNING', help="Log level messages (ERROR,WARNING,DEBUG,INFO...)"),
                    logfile: str = typer.Option(None, help="File to send logs to"),
                    save: str = typer.Option(None, help="Saves the output of this execution"),
                    plot: bool = typer.Option(False, help="Saves the plots"),
                    n: int = typer.Option(Config.N, help="Number of firms"),
                    t: int = typer.Option(Config.T, help="Time repetitions")):
    global model
    if t != model.config.T:
        model.config.T = t
    if n != model.config.N:
        model.config.N = n
    model.log.define_log(log, logfile)
    if plot:
        model.statistics.enable_plot = True
    if getconfig:
        print(model.config.__str__(separator="\n"))
        raise typer.Exit()
    manage_config_values(setconfig)
    run(save)


def run(save=None):
    global model
    model.run(export_datafile=save)


def manage_config_values(config_list):
    for item in config_list:
        try:
            name_config, value_config = item.split("=")
        except ValueError:
            model.log.error("A config value should be passed as name=value", before_start=True)
            raise typer.Exit(-1)
        try:
            getattr(model.config, name_config)
        except AttributeError:
            model.log.error(f"Configuration has no {name_config}", before_start=True)
            raise typer.Exit(-1)
        try:
            setattr(model.config, name_config, float(value_config))
        except ValueError:
            model.log.error(f"Value given {value_config} is not valid", before_start=True)
            raise typer.Exit(-1)


def is_notebook():
    try:
        __IPYTHON__
        return get_ipython().__class__.__name__ != "SpyderShell"
    except NameError:
        return False


model = Model()
if is_notebook():
    # if we are running in a Notebook:
    run()
else:
    # if we are running interactively:
    if __name__ == "__main__":
        typer.run(run_interactive)
