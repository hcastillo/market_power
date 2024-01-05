@echo off
pytest
python main.py --n 10 --t 100 --plot gretl
python experiment1.py
 
