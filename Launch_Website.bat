@echo off
title Stock Market Analyzer Web App
cls
echo ======================================================================
echo          LAUNCHING STOCK MARKET TICK DATA ANALYZER WEB APP
echo ======================================================================
echo.

cd /d "C:\Users\bneha\Documents\stock-market-analyzer"

echo [1/2] Opening Web Browser to http://localhost:8501 ...
start http://localhost:8501

echo [2/2] Starting Analytics Dashboard...
echo.
python -m streamlit run app.py --server.headless true --server.port 8501

pause
