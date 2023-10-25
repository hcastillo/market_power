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
    
          main.py --log DEBUG --n 150 --t 2000
    
    - When it is used as a package, the sequence should be:

          import market_power as mp
          model = mp.model.Model()
          model.config.configure( param=x )
          model.run()

  - *market_power.ipynb*: Notebook version

