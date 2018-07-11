rem set environment variables...
set PYTHONDIR=C:\Users\rhome\AppData\Local\Programs\Python\Python37-32
set PATH=%PATH%;%PYTHONDIR%;%PYTHONDIR%\Scripts\

rem start jupyter...
%PYTHONDIR%\python.exe ./solver.py
::%PYTHONDIR%\python.exe ./submit.py

pause