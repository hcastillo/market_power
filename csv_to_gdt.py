#!/usr/bin/env python
# coding: utf-8
"""
It opens a CSV with data generated from a pandas.DataFrame, it converts to GDT (Gretl file) and opens with gretl
@author: hector@bith.net
"""
import argparse
import os
import subprocess
import tempfile
import pandas as pd
import lxml.etree
import lxml.builder

class CsvToGdtParser:
    EXECUTABLE = 'C:\Program Files\gretl\gretl.exe'
    def __init__(self, filename, savefile):
        if os.name == 'nt':
            self.filename = filename.replace('/', '\\')
        else:
            self.filename = filename.replace('\\', '/')
        self.savefile = savefile
        if savefile:
            self.output = open(self.filename.replace(".csv", ".gdt"), "w")
        else:
            self.output = tempfile.NamedTemporaryFile(suffix=".gdt", mode="w", delete=False)

    def process(self):
        # generate from csv the result:
        if os.path.isfile(self.filename):
            data = pd.read_csv(self.filename, header=2)
            E = lxml.builder.ElementMaker()
            GRETLDATA = E.gretldata
            DESCRIPTION = E.description
            VARIABLES = E.variables
            VARIABLE = E.variable
            OBSERVATIONS = E.observations
            OBS = E.obs


            variables = VARIABLES(count=f"{len(data.keys())}")
            for i in data.keys():
                variables.append(VARIABLE(name=f"{i.strip()}"))
            observations = OBSERVATIONS(count=f"{len(data)}", labels="false")
            for i in range(len(data)):
                string_obs = data[i:i+1].to_string().split('\n')
                observations.append(OBS(string_obs[1][4:]))
            gdt_result=GRETLDATA(
                         DESCRIPTION("Datos importados, 2024"),
                           variables,
                           observations,
                           version="1.4", name='prueba', frequency="special:1", startobs="1",
                           endobs="1000", type="time-series"
                        )
            self.output.write(
                '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE gretldata SYSTEM "gretldata.dtd">\n')
            self.output.write(
                lxml.etree.tostring(gdt_result, pretty_print=True, encoding=str))
            self.output.close()
        else:
            raise FileNotFoundError(self.filename)

    def execute(self):
        if not self.savefile:
            if os.path.exists(self.EXECUTABLE):
                subprocess.run([self.EXECUTABLE, self.output.name], stdout=subprocess.DEVNULL, shell=True)

    def close(self):
        if not self.savefile:
            os.remove(self.output.name)

# noinspection SpellCheckingInspection
def run_interactive():
    parser = argparse.ArgumentParser(description="Convert a GDT file")
    parser.add_argument('--save', default=False, action=argparse.BooleanOptionalAction,
                        help="Store in the same directory as the origin with the gdt result file")
    args, files = parser.parse_known_args()
    for filename in files:
        parser = CsvToGdtParser(filename, args.save)
        parser.process()
        parser.execute()

if __name__ == "__main__":
    run_interactive()
