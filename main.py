#!/usr/bin/env python
# coding: utf-8
"""
ABM model executer, to run interactively the model
@author: hector@bith.net
"""
from market_power.model import Model
from market_power.config import Config
import typer


def run_interactive(log: str = typer.Option('ERROR', help="Log level messages (ERROR,DEBUG,INFO...)"),
                    logfile: str = typer.Option(None, help="File to send logs to"),
                    save: str = typer.Option(None, help="Saves the output of this execution"),
                    n: int = typer.Option(Config.N, help="Number of firms"),
                    t: int = typer.Option(Config.T, help="Time repetitions")):
    global model
    if t != model.config.T:
        model.config.T = t
    if n != model.config.N:
        model.config.N = n
    model.log.define_log(log, logfile)
    run(save)


def run(save=None):
    global model
    model.run(export_datafile=save)


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
