@echo off
title Stock Market Tick Data Analyzer
cls

:MENU
echo ======================================================================
echo                STOCK MARKET TICK DATA ANALYZER
echo ======================================================================
echo.
echo  [1] Run Full Pipeline (Fetch Data, Seed MongoDB, Run Queries & PDF)
echo  [2] Launch Interactive Web Dashboard (Streamlit GUI)
echo  [3] Open Generated PDF Project Report
echo  [4] Exit
echo.
echo ======================================================================
set /p choice="Select an option (1-4): "

if "%choice%"=="1" (
    echo.
    echo Running Master Pipeline...
    python main.py
    pause
    goto MENU
)

if "%choice%"=="2" (
    echo.
    echo Launching Interactive Dashboard in your default web browser...
    python -m streamlit run app.py
    pause
    goto MENU
)

if "%choice%"=="3" (
    echo.
    if exist reports\Stock_Market_Analyzer_Report.pdf (
        start reports\Stock_Market_Analyzer_Report.pdf
    ) else (
        echo Report not found! Please run Option 1 first to generate the report.
    )
    pause
    goto MENU
)

if "%choice%"=="4" (
    echo Exiting...
    exit /b
)

echo Invalid choice! Please select 1, 2, 3, or 4.
pause
goto MENU
