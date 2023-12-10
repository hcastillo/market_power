#!/usr/bin/env python
# coding: utf-8
"""
ABM model tests to verify the functions inside firm
@author: hector@bith.net
"""
import pytest
from market_power.model import Model
from market_power.firm import Firm
from util.stats_array import StatsFirms, PlotMethods
import numpy as np
import os

class TestPlot:
    @pytest.fixture
    def array_to_plot(self):
        model = Model()
        model.test = True
        model.configure(N=2, T=5, w=0.005, alpha=0.08, eta=0.000001, phi=1.1, beta=0.02, g=1.1, k=1, b=1, m=0)

        array = StatsFirms(model, float, "description", "short", prepend="^")
        array.data = np.array([5, 4, 3, 8, 12])
        yield array
        # teardown
        array = None

    def plot_a_figure(self, array_to_plot):
        file_generated = array_to_plot.model.statistics.OUTPUT_DIRECTORY+"/firms_"+"description.png"

        assert os.path.isfile(file_generated), False
        array_to_plot.plot(PlotMethods.pyplot)
        assert os.path.isfile(file_generated), True
        os.remove(file_generated)

    def plot_three_figures(self, array_to_plot):
        array1 = StatsFirms(array_to_plot.model, float, "other1", "name1", prepend="#")
        array2 = StatsFirms(array_to_plot.model, float, "other2", "name1", prepend="#")
        array_multiple = [array_to_plot, array1, array2]
        file0_generated = array_to_plot.model.statistics.OUTPUT_DIRECTORY+"/firms_"+"description.png"
        file1_generated = array_to_plot.model.statistics.OUTPUT_DIRECTORY+"/firms_"+"description.png"
        file2_generated = array_to_plot.model.statistics.OUTPUT_DIRECTORY+"/firms_"+"description.png"
        file_global = array_to_plot.model.statistics.OUTPUT_DIRECTORY+"/firms_"+"description.png"
        assert os.path.isfile(file_global), False
        assert os.path.isfile(file0_generated), False
        assert os.path.isfile(file1_generated), False
        assert os.path.isfile(file2_generated), False
        array_to_plot.plot(PlotMethods.pyplot, multiple=array_multiple)
        assert os.path.isfile(file_global), True
        assert os.path.isfile(file0_generated), True
        assert os.path.isfile(file1_generated), True
        assert os.path.isfile(file2_generated), True
        os.remove(file_global)
        os.remove(file0_generated)
        os.remove(file1_generated)
        os.remove(file2_generated)
