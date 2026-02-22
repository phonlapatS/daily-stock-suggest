import os
import sys
import subprocess

# Redirect to the new location
NEW_PATH = os.path.join(os.path.dirname(__file__), "core_reports", "daily_forecast_dashboard.py")

if __name__ == "__main__":
    if not os.path.exists(NEW_PATH):
        print(f"❌ Error: Script not found at {NEW_PATH}")
        sys.exit(1)
        
    cmd = [sys.executable, NEW_PATH] + sys.argv[1:]
    subprocess.run(cmd)
