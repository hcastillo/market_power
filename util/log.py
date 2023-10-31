#!/usr/bin/env python
# coding: utf-8
"""
ABM model auxiliary file: logging facilities
@author: hector@bith.net
"""
import logging
import numpy as np


class Log:
    """
    The class acts as a logger and helpers to represent the data and evol from the Model.
    """
    logger = logging.getLogger("model")
    model = None
    logLevel = "ERROR"

    def __init__(self, its_model):
        self.model = its_model

    @staticmethod
    def format(number):
        if isinstance(number, int) or isinstance(number, np.int32):
            result = f"{number:3}"
        else:
            result = f"{number:5.2f}"
            while len(result) > 5 and result[-1] == "0":
                result = result[:-1]
            while len(result) > 5 and result.find('.') >= 0:
                result = result[:-1]
        return result

    @staticmethod
    def get_level(option):
        try:
            return getattr(logging, option.upper())
        except AttributeError:
            logging.error(f" '--log' must contain a valid logging level and {option.upper()} is not.")
            sys.exit(-1)

    def debug(self, text, before_start=False):
        time_instant = "     " if before_start else f"t={self.model.t:03}"
        self.logger.debug(f"{time_instant} {text}")

    def info(self, text):
        self.logger.info(f" t={self.model.t:03} {text}")

    def error(self, text):
        self.logger.error(f"t={self.model.t:03} {text}")

    def define_log(self, log: str, logfile: str = ''):
        formatter = logging.Formatter('%(levelname)s %(message)s')
        self.logLevel = Log.get_level(log.upper())
        self.logger.setLevel(self.logLevel)
        if logfile:
            if not logfile.startswith(Statistics.OUTPUT_DIRECTORY):
                logfile = f"{Statistics.OUTPUT_DIRECTORY}/{logfile}"
            fh = logging.FileHandler(logfile, 'a', 'utf-8')
            fh.setLevel(self.logLevel)
            fh.setFormatter(formatter)
            self.logger.addHandler(fh)
        else:
            ch = logging.StreamHandler()
            ch.setLevel(self.logLevel)
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)
