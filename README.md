# Market Power ABM
An Agent Based Model based on Dixit-Greenwald-Sitglitz model of monopolistic competition


- Auxiliary files:
  - *requirements.txt*: list of the necessary python packages
  - *util/statistics.py*: class for managing the output 
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
    - To view all the config you can modify from command line, use --getconfig
    
    - When it is used as a package, the sequence should be:

          import market_power as mp
          model = mp.model.Model(bank_sector_A_i0=20, firms_A_i0=2)
          model.run()

  - *market_power.ipynb*: Notebook version


- Command line options:
  - *./main.py --log-what firms_K,firms_A*: executes in level INFO showing for each firm K and A
  - *./main.py --log DEBUG*: executes in maximum level of detail with also all the operations done for each firm/step
  - *./main.py --log WARNING*: a minimum level of details: for each step, the summary of firms and bank sector state
  - *./main.py --logfile xxx*: sends the log output to a file instead to screen
  - *./main.py --save xxx*: saves in text file the model output (not the log)
  - *./main.py --plot bokeh*: instead of saving a text file with the output, creates a plot with Bokeh