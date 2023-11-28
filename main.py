#!/usr/bin/env python
# coding: utf-8
"""
ABM model executer, to run interactively the modelss
@author: hector@bith.net
"""
from market_power.model import Model
from market_power.config import Config
import typer
from typing import List


def run_interactive(config: List[str] = typer.Argument(None, help="Change config value (i.e. alpha=3.1, ? to list)"),
                    log: str = typer.Option(None, help="Log level messages (ERROR,WARNING,INFO,DEBUG)"),
                    logfile: str = typer.Option(None, help="File to send the logs to"),
                    log_what: str = typer.Option(None, help="What to log (apart from balance, ? to list)"),
                    save: str = typer.Option(None, help="Save the output of this execution"),
                    plot: str = typer.Option(None, help="Save the plot (? to list formats)"),
                    plot_tmin: int = typer.Option(None, help="Min. time to represent in the plots"),
                    plot_tmax: int = typer.Option(None, help="Max. time to represent in the plots"),
                    plot_what: str = typer.Option("", help="What to plot (all by default, ? to list)"),
                    n: int = typer.Option(Config.N, help="Number of firms"),
                    t: int = typer.Option(Config.T, help="Time repetitions")):
    global model
    if t != model.config.T:
        model.config.T = t
    if n != model.config.N:
        model.config.N = n
    if log_what and not log:
        log = "INFO"
    if not log:
        log = "WARNING"
    if log_what == '?' or plot_what == '?':
        list_what()
    else:
        model.log.define_log(log=log, logfile=logfile, what=log_what)
    if (plot_tmin or plot_tmax or plot_what) and not plot:
        # if not enabled plot with an specific format, we assume the first type: pyplot
        plot = model.statistics.get_plot_formats()[0]
    if config:
        if config == '?':
            print(model.config.__str__(separator="\n"))
            raise typer.Exit()
        else:
            manage_config_values(config)
    if plot:
        if plot == '?':
            model.statistics.get_plot_formats(display=True)
            raise typer.Exit()
        else:
            if plot.lower() in model.statistics.get_plot_formats():
                model.statistics.enable_plotting(plot_format=plot.lower(), plot_min=plot_tmin,
                                                 plot_max=plot_tmax, plot_what=plot_what)
            else:
                model.log.error(f"Plot format must be one of {model.statistics.get_plot_formats()}", before_start=True)
                raise typer.Exit(-1)
    run(save)


def run(save=None):
    global model
    model.run(export_datafile=save)


def list_what():
    global model
    model.initialize_model(export_datafile="mock")
    model.statistics.get_what()
    raise typer.Exit()


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
    model.statistics.enable_plotting(plot_format="screen")
    model.statistics.interactive = False
    run()
else:
    # if we are running interactively:
    if __name__ == "__main__":
        typer.run(run_interactive)
