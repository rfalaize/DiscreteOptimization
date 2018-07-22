rem set environment variables...
set PYTHONDIR=C:\Users\rhome\AppData\Local\Programs\Python\Python36
set PATH=%PATH%;%PYTHONDIR%;%PYTHONDIR%\Scripts\

rem start jupyter...
::%PYTHONDIR%\python.exe ./solver.py ./data/ks_10000_0
%PYTHONDIR%\python.exe ./submit.py
::jupyter-notebook.exe

pause