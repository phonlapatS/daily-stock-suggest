import subprocess
import time
import sys

def run_script(script_name, description):
    print(f"\n{'='*60}")
    print(f"🚀 RUNNING: {description}")
    print(f"   Script: {script_name}")
    print(f"{'='*60}")
    
    start_time = time.time()
    try:
        # Run the script and wait for it to finish
        result = subprocess.run([sys.executable, script_name], check=True)
        
        elapsed = time.time() - start_time
        print(f"\n✅ FINISHED: {description} (Time: {elapsed:.2f}s)")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ FAILED: {description}")
        print(f"   Error: {e}")
        return False

def main():
    print("🎯 STARTING DAILY ROUTINE V4.3")
    print("   (Prediction -> Check -> Report -> Performance -> Dashboard)")
    
    # 1. Prediction (Main)
    if not run_script("main.py", "1. Market Scan & Prediction"):
        return

    # 2. Performance Check (Yesterday's results)
    if not run_script("scripts/check_forward_testing.py", "2. Verify Previous Predictions"):
        return

    # 3. Forward Testing Report (Detailed logs)
    if not run_script("scripts/forward_testing_report.py", "3. Generate Forward Test Report"):
        return

    # 4. Calculate Performance (P/L)
    if not run_script("scripts/calculate_performance.py", "4. Calculate Performance (P/L)"):
        return
        
    # 5. Dashboard (Overview)
    if not run_script("scripts/daily_forecast_dashboard.py", "5. Daily Forecast Dashboard"):
        return
        
    # Optional: Bonus Summary (N+1 Voting)
    print("\n💡 Tip: Run 'python scripts/generate_summary.py' for N+1 Voting Analysis")

    print("\n🎉 DAILY ROUTINE COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    main()
