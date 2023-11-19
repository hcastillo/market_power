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


class Log:
    """
    The class acts as a logger and helpers to represent the data and evol from the Model.
    """
    logger = logging.getLogger("model")
    model = None
    log_level = "ERROR"
    only_errors = True
    progress_bar = None

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

    def error(self, text, before_start=False):
        if not self.model.test:
            self.logger.error(f"{self.__format_t__(before_start)} {text}")

    def __format_t__(self, before_start=False):
        return "     " if before_start else f"t={self.model.t:03}"

    def define_log(self, log: str, logfile: str = ''):
        formatter = logging.Formatter('%(levelname)s %(message)s')
        self.log_level = Log.get_level(log.upper())
        self.only_errors == log == "ERROR"
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

    def initialize_model(self):
        if not self.model.test:
            self.info(self.model.statistics.current_status_save(), before_start=True)
            if self.only_errors:
                self.progress_bar = Bar('Executing model', max=self.model.config.T)

    def step(self, log_info):
        if not self.model.test:
            if self.only_errors and self.progress_bar:
                self.progress_bar.next()
            else:
                self.info(log_info)

    def finish_model(self):
        if not self.model.test:
            if self.only_errors and self.progress_bar:
                self.progress_bar.finish()
            else:
                self.info(f"finish: model T={self.model.config.T} N={self.model.config.N}")


