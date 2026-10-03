@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
    py -3 run.py
    if errorlevel 1 pause
    exit /b
)
where python >nul 2>nul
if not errorlevel 1 (
    python run.py
    if errorlevel 1 pause
    exit /b
)
echo Can cai Python 3.10 tro len co Tcl/Tk tu https://www.python.org/downloads/windows/
echo Sau khi cai dat, mo lai tep nay.
pause

