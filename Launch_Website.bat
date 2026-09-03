@echo off
title Stock Market Analyzer Web Launcher
cls
echo ======================================================================
echo          LAUNCHING STOCK MARKET TICK DATA ANALYZER WEB APP
echo ======================================================================
echo.

cd /d "C:\Users\bneha\Documents\stock-market-analyzer"

echo [1/2] Opening Web Browser to http://localhost:5000 ...
start http://localhost:5000

echo [2/2] Starting Flask & HTML5 Web Server...
echo.
python server.py

pause
