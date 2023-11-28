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


class TermColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Log:
    """
    The class acts as a logger and helpers to represent the data and evol from the Model.
    """
    logger = logging.getLogger("model")
    model = None
    log_level = "WARNING"
    progress_bar = None
    what_keywords = []

    def __init__(self, its_model):
        self.model = its_model

    @staticmethod
    def format(number):
        if isinstance(number, int) or isinstance(number, np.int32):
            result = f"{number:3}"
        else:
            result = f"{number:5.2f}"
            while len(result) > 5 and result[-1] in "0":
                result = result[:-1]
            while len(result) > 5 and result.find('.') > 0:
                result = result[:-1]
        return result if result[-1] != '.' else f' {result[:-1]}'

    @staticmethod
    def get_level(option):
        try:
            return getattr(logging, option.upper())
        except AttributeError:
            logging.error(f" '--log' must contain a valid logging level and {option.upper()} is not.")
            sys.exit(-1)

    def debug(self, text, before_start=False):
        if not self.model.test:
            self.logger.debug(f"{self.__format_t__(before_start)} {text}")

    def info(self, text, before_start=False):
        if not self.model.test:
            self.logger.info(f" {self.__format_t__(before_start)} {text}")

    def warning(self, text, before_start=False):
        if not self.model.test:
            self.logger.warning(f" {self.__format_t__(before_start)} {text}")

    def error(self, text, before_start=False):
        if not self.model.test:
            self.logger.error(f"{TermColors.FAIL}{self.__format_t__(before_start)} {text}{TermColors.ENDC}")

    def __format_t__(self, before_start=False):
        return "     " if before_start else f"t={self.model.t:03}"

    def define_log(self, log: str, logfile: str = '', what=""):
        formatter = logging.Formatter('%(levelname)s %(message)s')
        self.log_level = Log.get_level(log.upper())
        if what:
            self.what_keywords = what.split(",")
        if self.log_level > Log.get_level("WARNING") and self.model.statistics.interactive:
            self.progress_bar = Bar('Executing model', max=self.model.config.T)
        self.logger.setLevel(self.log_level)
        if logfile:
            if not logfile.startswith(self.model.statistics.OUTPUT_DIRECTORY):
                logfile = f"{self.model.statistics.OUTPUT_DIRECTORY}/{logfile}"
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
        text = f"{firm.__str__()}  " # K={Log.format(firm.K)}"
        # text += f" | A={Log.format(firm.A)} L={Log.format(firm.L)}"
        if not before_start: #TODO
            if self.what_keywords:
                for elem in self.model.statistics.data:
                    if elem in self.what_keywords and elem.startswith('firms'):
                        text += f" {elem}={self.model.statistics.data[elem].get_value(firm)}"
                        #self.get_value(getattr(firm, self.attr_name))
        self.info(text, before_start)

    def initialize_model(self):
        if not self.model.test:
            self.warning(self.model.statistics.current_status_save(), before_start=True)

    def step(self, log_info):
        if not self.model.test:
            if self.progress_bar:
                self.progress_bar.next()
            else:
                self.warning(log_info)
                self.model.statistics.info_status(before_start=False)

    def finish_model(self):
        if not self.model.test:
            if self.progress_bar:
                self.progress_bar.finish()
            else:
                self.info(f"finish: model T={self.model.config.T} N={self.model.config.N}")
