import os
import sys
import subprocess

# Redirect to the new location
# Note: User previously re-created check_forward_testing.py in scripts/
# We are making this a shim to the one in core_reports/ for consistency, 
# but ensuring the one in core_reports is fixed first.
NEW_PATH = os.path.join(os.path.dirname(__file__), "core_reports", "check_forward_testing.py")

if __name__ == "__main__":
    if not os.path.exists(NEW_PATH):
        print(f"❌ Error: Script not found at {NEW_PATH}")
        sys.exit(1)
        
    cmd = [sys.executable, NEW_PATH] + sys.argv[1:]
    subprocess.run(cmd)
