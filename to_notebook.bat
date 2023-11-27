@echo off


mkdir auxiliar
if %errorlevel%==0 (
  copy market_power\*.py auxiliar
  copy util\*.py auxiliar
  findstr /v /c:"from util." market_power\model.py  | findstr /v /c:"from market_power." > auxiliar\model.py
  findstr /v /c:"from market_power." main.py > auxiliar\main.py
  findstr /v /c:"from util." util\statistics.py | findstr /v /c:"from progress.bar" | findstr /v /c:"from market_power." > auxiliar\statistics.py
  findstr /v /c:"from progress.bar" util\log.py | findstr /v /c:"from market_power." > auxiliar\log.py

  cd auxiliar
  jupytext *.py --to ipynb 
  nbmerge config.ipynb bank.ipynb firm.ipynb log.ipynb stats_array.ipynb statistics.ipynb model.ipynb main.ipynb -o ..\market_power.ipynb
  cd ..

  del auxiliar\*.py 
  del auxiliar\*.ipynb
  rmdir auxiliar
)

python -m unittest discover -s tests
if %errorlevel%==0 (
 git add .
 git commit -a
 git push
)