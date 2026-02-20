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
    print("🎯 STARTING V4.3 PREDICTION ROUTINE")
    print("   (N+1 Prediction -> Performance Log -> Forward Test Report)")
    
    # 1. Main Prediction (N+1 Prediction Strategy)
    #    - Scans market
    #    - Generates predictions for tomorrow
    if not run_script("main.py", "1. Market Scan & N+1 Prediction"):
        return

    # 2. Performance Logging (Check previous predictions)
    #    - Verifies yesterday's predictions against today's close
    #    - Updates forward_testing_log.csv
    if not run_script("scripts/check_forward_testing.py", "2. Performance Verification"):
        return

    # 3. Forward Testing Report
    #    - Summarizes win/loss stats
    #    - Generates report summary
    if not run_script("scripts/forward_testing_report.py", "3. Forward Testing Report"):
        return

    # Optional: Summary of Bias
    if not run_script("scripts/generate_summary.py", "4. Stock Bias Summary (N+1 Voting)"):
        return

    print("\n🎉 ALL TASKS COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    main()
