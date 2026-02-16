@echo off
REM Quick script to run China realistic settings test

echo ====================================================================
echo Running China Realistic Settings Test
echo ====================================================================
echo.

REM Clean old results
echo Step 1: Cleaning old results...
python scripts/fix_test_china.py
echo.

REM Run test
echo Step 2: Running test...
echo This will take 30-60 minutes for 18 combinations
echo.
python scripts/test_china_realistic_settings.py

echo.
echo ====================================================================
echo Test Complete!
echo ====================================================================
echo.
echo Results saved to: data/china_realistic_settings_results.csv
echo.
pause

