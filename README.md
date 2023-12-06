# Market Power ABM
An Agent Based Model based on Dixit-Greenwald-Sitglitz model of monopolistic competition


- Auxiliary files:
  - *requirements.txt*: list of the necessary python packages
  - *util/statistics.py*: class for managing the output 
  - *util/stats_array.py*: it contains the code to plot with pyplot, bokeh, grace and gretl. 
  - *util/log.py*: class for managing the logging
  - *output/&ast;*: the files generated (plots mainly)
  - *test/&ast;*: unit tests

- The ABM model:
  - *market_power/model.py*: the model itself, with the sequence of execution
  - *market_power/firm.py*: the firms definition
  - *market_power/bank.py*: the bank sector
  - *market_power/config.py*: with all the fixed parameters
  - *main.py*: use to execute from command line the simulation.
    - It accepts options. For instance, you can execute this:
    
          main.py --log DEBUG --n 150 --t 2000 bank_sector_A_i0=20
    - To view all the config you can modify from command line, use '?'
    - To run two models and obtain a combined plot, repeat twice a config parameter, for instance:
    
          main.py --log DEBUG --n 150 --t 2000 eta=0.0001 eta=0.25 --plot
      It will execute two models and generate individual files for each model but also a combined version to compare both. The individual files will be prepend with "1" and the combined version without it.
    - The model can be executed as a package. To do it, the sequence should be:

          import market_power as mp
          model = mp.model.Model(bank_sector_A_i0=20, firms_A_i0=2)
          model.run() # it will return the array with the results

    - *market_power.config*: If it is present, and the file contains sections as this, that program is called to open plots after generate them:
    
          [agr]
          program=C:\program files\qtgrace\qtgrace.exe # Grace for windows
          [gdt] 
          program=.... # for Gretl
          [html]
          program=default  # to open with default program in the system for html files generated for Bokeh format
          [png]
          program=default  # same for PNG of pyplot, the default system
  - *market_power.ipynb*: Notebook version. It is a combined version of all the files generated in Windows using *to_notebook.bat*.


- Command line options:
  - *./main.py --log-what firms_K,firms_A*: executes in level INFO showing for each firm K and A
  - *./main.py --log DEBUG*: executes in maximum level of detail with also all the operations done for each firm/step
  - *./main.py --log WARNING*: a minimum level of details: for each step, the summary of firms and bank sector state
  - *./main.py --logfile xxx*: sends the log output to a file instead to screen
  - *./main.py --save xxx*: saves in text file the model output (not the log)
  - *./main.py --plot bokeh*: instead of saving a text file with the output, creates a plot with Bokeh