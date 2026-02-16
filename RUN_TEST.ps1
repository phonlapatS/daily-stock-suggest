# PowerShell script to run China realistic settings test

Write-Host "===================================================================="
Write-Host "Running China Realistic Settings Test"
Write-Host "===================================================================="
Write-Host ""

# Clean old results
Write-Host "Step 1: Cleaning old results..."
python scripts/fix_test_china.py
Write-Host ""

# Run test
Write-Host "Step 2: Running test..."
Write-Host "This will take 30-60 minutes for 18 combinations"
Write-Host ""
python scripts/test_china_realistic_settings.py

Write-Host ""
Write-Host "===================================================================="
Write-Host "Test Complete!"
Write-Host "===================================================================="
Write-Host ""
Write-Host "Results saved to: data/china_realistic_settings_results.csv"
Write-Host ""

