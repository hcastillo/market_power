#!/usr/bin/env python
# coding: utf-8
import pandas as pd

model = pd.read_csv('model.csv', header=2)

elements = model.keys()[6:-1]
for i in range(len(elements)):
    for j in range(i + 1, len(elements)):
        ai = model[elements[i]]
        aj = model[elements[j]]
        for t in (0,1,-1,2,-2,5,-5,10,-10):
            if ai.corr(aj.shift(t)) > 0.75:
                print(elements[i], elements[j], ai.corr(aj.shift(t)),t)
        # if ai.corr(aj) > 0.75:
        #     print(elements[i], elements[j], ai.corr(aj))
        # if ai.corr(aj.shift(-1)) > 0.75:
        #     print(elements[i], elements[j], ai.corr(aj.shift(-1)), -1)
