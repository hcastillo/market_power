#!/usr/bin/env python
# coding: utf-8
"""
ABM model auxiliary file: logging facilities
@author: hector@bith.net
"""
import logging
import numpy as np
import sys
from progress.bar import Bar
from util.stats_array import PlotMethods


class Log:
    """
    The class acts as a logger and helpers for the Model.
    """
    logger = logging.getLogger("model")
    OUTPUT_DIRECTORY = "output"
    model = None
    log_level = "WARN"  # default if not other chosen
    progress_bar = None
    what_keywords = []
    only_firms_or_bank = False

    def __init__(self, model):
        self.model = model
        self.colors = LogColors()

    def set_model(self, its_model, plot, num_model, multiple_models_will_be_run: False):
        if not self.what_keywords and its_model.log.what_keywords:
            self.what_keywords = its_model.log.what_keywords
        self.model = its_model
        self.model.statistics.do_plot
        if multiple_models_will_be_run:
            self.model.export_datafile = f"{self.OUTPUT_DIRECTORY}/model_{num_model}.txt"
            self.model.statistics.export_datafile = self.model.export_datafile
            self.model.statistics.interactive = False
            self.model.statistics.multiple = True
        else:
            if plot == PlotMethods.gretl and not self.model.export_datafile:
                self.model.export_datafile = f"{self.OUTPUT_DIRECTORY}/model.txt"
            self.model.statistics.interactive = True
            self.model.statistics.multiple = False
        self.model.log = self

    @staticmethod
    def format(number):
        if isinstance(number, int) or isinstance(number, np.int32):
            result = f"{number:4}"
        else:
            result = f"{number:7.3f}"
            while len(result) > 7 and result[-1] in "0":
                result = result[:-1]
            while len(result) > 7 and result.find('.') > 0:
                result = result[:-1]
        if len(result)>7:
            result = f"{number:.3E}".replace("E+0","e").replace("E+","e")
        return result if result[-1] != '.' else f' {result[:-1]}'

    @staticmethod
    def get_level(option):
        if option == "?":
            for level in list(logging._nameToLevel.keys()):
                if hasattr(Log, level.lower()):
                    print(f"\t{level}", "(default)" if level == Log.log_level else "")
            sys.exit(0)

        try:
            return getattr(logging, option.upper())
        except AttributeError:
            logging.error(f" '--log' must contain a valid logging level and {option.upper()} is not.")
            sys.exit(-1)

    def debug(self, text, before_start=False):
        if text and not self.model.test:
            self.logger.debug(f"{self.__format_t__(before_start)} {text}")

    def info(self, text, before_start=False):
        if text and not self.model.test:
            self.logger.info(f" {self.__format_t__(before_start)} {text}")

    def warning(self, text, before_start=False):
        if text and not self.model.test:
            self.logger.warning(f" {self.__format_t__(before_start)} {text}")

    def error_minor(self, text, before_start=False):
        if text and not self.model.test and not self.progress_bar:
            self.logger.error(f" {self.__format_t__(before_start)} {text}")

    def error(self, text, before_start=False):
        if text:
            self.logger.error(self.colors.fail(f"{self.__format_t__(before_start)} {text}"))

    def __format_t__(self, before_start=False):
        return f"     {self.model.get_id(short=True)}" if before_start \
            else f"t={self.model.t + 1:03}{self.model.get_id(short=True)}"

    def define_log(self, log: str, logfile: str = '', what=[]):
        # noinspection SpellCheckingInspection
        formatter = logging.Formatter('%(levelname)s %(message)s')
        self.log_level = Log.get_level(log.upper())
        self.what_keywords = what
        self.logger.setLevel(self.log_level)
        if self.logger.hasHandlers():
            self.logger.handlers.clear()
        if logfile:
            if not logfile.startswith(self.OUTPUT_DIRECTORY):
                logfile = f"{self.OUTPUT_DIRECTORY}/{self.model.get_id_for_filename()}{logfile}"
            else:
                logfile = f"{self.model.get_id_for_filename()}{logfile}"
            fh = logging.FileHandler(logfile, 'a', 'utf-8')
            fh.setLevel(self.log_level)
            fh.setFormatter(formatter)
            self.logger.addHandler(fh)
        else:
            ch = logging.StreamHandler()
            ch.setLevel(self.log_level)
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

    def info_firm(self, firm, before_start=False):
        text = f"{firm.__str__()}  "
        if not before_start:
            if self.what_keywords and not self.model.test:
                for elem in self.model.statistics.data:
                    if elem in self.what_keywords and elem.startswith('firms'):
                        text += f" {elem.replace('firms_', '')}="
                        text += f"{self.format(self.model.statistics.data[elem].get_value(firm))}"
                self.info(text, before_start)

    def initialize_model(self):
        if self.logger.level == Log.get_level("ERROR") and not self.model.test:
            self.progress_bar = Bar(f"Executing {self.model.get_id()}", max=self.model.config.T)

    def step(self, log_info, before_start=False):
        if not self.model.test and self.model.statistics.interactive:
            if self.progress_bar:
                self.progress_bar.next()
            else:
                self.warning(log_info, before_start=before_start)
                self.model.statistics.info_status(before_start=before_start)

    def finish_model(self):
        if not self.model.test:
            if self.progress_bar:
                self.progress_bar.finish()
            else:
                extra_info = "" if not self.model.abort_execution else "ABORTED EXECUTION "
                self.info(f"{extra_info}finish: {self.model.get_id()} {self.model.model_title}" +
                          f"T={self.model.config.T} N={self.model.config.N} " +
                          f"bank_failures={self.model.bank_sector.bank_failures}")


class LogColors:
    colors = True

    def warning(self, text):
        if self.colors:
            import colorama
            return colorama.Fore.YELLOW + text + colorama.Fore.RESET

    def fail(self, text):
        if self.colors:
            import colorama
            return colorama.Fore.RED + text + colorama.Fore.RESET

    def remark(self, text):
        if self.colors:
            import colorama
            return colorama.Style.BRIGHT + text + colorama.Style.NORMAL

    def __init__(self):
        try:
            import colorama
        except ImportError:
            self.colors = False
        else:
            colorama.init(autoreset=True)
