@echo off


mkdir auxiliar
if %errorlevel%==0 (
  copy market_power\*.py auxiliar
  copy util\*.py auxiliar
  findstr /v "from util." market_power\model.py  | findstr /v "from market_power." > auxiliar\model.py
  findstr /v "from market_power." main.py > auxiliar\main.py
  findstr /v "from util." util\statistics.py > auxiliar\statistics.py

  cd auxiliar
  jupytext *.py --to ipynb 
  nbmerge config.ipynb bank.ipynb firm.ipynb model.ipynb log.ipynb statistics.ipynb main.ipynb -o ..\market_power.ipynb
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