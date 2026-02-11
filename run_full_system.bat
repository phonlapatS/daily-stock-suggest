@echo off
echo ======================================================================
echo 🚀 STARTING FULL SYSTEM BACKTEST (ALL MARKETS)
echo ======================================================================
echo.
echo 1. Running Backtest on ALL Assets (History: 5000 bars)
echo    This may take a while depending on internet speed...
echo.

python scripts/backtest.py --full --bars 5000

echo.
echo ======================================================================
echo 2. Generating Metrics Report
echo    - Thai: Prob > 60%% | RR > 1.5
echo    - Global: Prob > 50%% | RR > 1.0
echo ======================================================================
echo.

python scripts/calculate_metrics.py

echo.
echo ======================================================================
echo ✅ PROCESS COMPLETE!
echo    Check report above or open data/symbol_performance.csv
echo ======================================================================
pause
