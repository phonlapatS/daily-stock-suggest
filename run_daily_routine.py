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
    print("=" * 60)
    print("🎯 PREDICT N+1 MASTER ROUTINE - V4.4.7")
    print("   (Scan + Verify -> Report -> Dashboard)")
    print("=" * 60)
    
    # 1. Main Engine (Scan + Verify)
    if not run_script("main.py", "1. Main Scan & Consensus Engine"):
        return

    # 2. Consensus Summary Report
    # We use the shim or the direct path. Let's use the direct path with arguments.
    print(f"\n{'='*60}")
    print(f"🚀 RUNNING: 2. V4.4 Consensus Summary (ALL)")
    print(f"   Script: scripts/core_reports/view_report.py")
    print(f"{'='*60}")
    try:
        subprocess.run([sys.executable, "scripts/core_reports/view_report.py", "ALL"], check=True)
    except Exception as e:
        print(f"⚠️ Report display issue: {e}")

    # 3. Executive Dashboard
    if not run_script("scripts/core_reports/daily_forecast_dashboard.py", "3. Executive Dashboard"):
        print("⚠️ Dashboard could not be generated.")

    print("\n" + "=" * 60)
    print("🎉 V4.4.7 DAILY ROUTINE COMPLETED SUCCESSFULLY!")
    print("   ผลลัพธ์ถูกบันทึกที่: data/forecast_tomorrow.csv")
    print("   ประวัติถูกบันทึกที่: logs/performance_log.csv")
    print("=" * 60)

if __name__ == "__main__":
    main()
