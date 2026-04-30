@echo off
:: ──────────────────────────────────────────────────────
::  ExpensePredict AI — Launcher
::  Fixes "Could not find platform independent libraries" warning
:: ──────────────────────────────────────────────────────

:: Set Python home to the actual installation directory
set PYTHONHOME=C:\Users\shivam\AppData\Local\Programs\Python\Python314

:: Include the parent folder's site-packages where Flask was installed
set PYTHONPATH=C:\Users\shivam\OneDrive\Documents\shivam proj\Lib\site-packages

:: Change into the app directory
cd /d "%~dp0"

echo.
echo  ==========================================
echo   ExpensePredict AI  ^|  Starting Server...
echo  ==========================================
echo   URL : http://127.0.0.1:5000
echo   Press CTRL+C to stop the server.
echo  ==========================================
echo.

C:\Python314\python.exe app.py

pause
