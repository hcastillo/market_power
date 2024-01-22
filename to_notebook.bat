@echo off


mkdir auxiliar
if %errorlevel%==0 (
  copy market_power\*.py auxiliar
  copy util\*.py auxiliar
  findstr /v /c:"from util." market_power\model.py  | findstr /v /c:"from market_power." > auxiliar\model.py
  findstr /v /c:"from market_power." main.py | findstr /v /c:"from util."  > auxiliar\main.py
  findstr /v /c:"from util." util\stats.py | findstr /v /c:"from progress.bar" | findstr /v /c:"from market_power." > auxiliar\stats.py
  findstr /v /c:"from progress.bar" util\log.py | findstr /v /c:"from util." | findstr /v /c:"from market_power." > auxiliar\log.py
  findstr /v /c:"from market_power." util\utilities.py > auxiliar\utilities.py
  cd auxiliar
  jupytext *.py --to ipynb 
  nbmerge config.ipynb bank.ipynb firm.ipynb log.ipynb stats_array.ipynb stats.ipynb utilities.ipynb model.ipynb main.ipynb -o ..\market_power.ipynb
  cd ..

  del auxiliar\*.py 
  del auxiliar\*.ipynb
  rmdir auxiliar
)
