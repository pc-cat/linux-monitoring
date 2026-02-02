import time
import os
import sys

# Ensure Python can find the 'modules' folder
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from modules.monitor_directory import DirectoryMonitor
from modules.monitor_system import SystemMonitor
from modules.reports_generator import ReportGenerator

# --- CONFIGURATION ---
# Change this path to the folder you want to monitor!
WATCH_DIRECTORY = os.path.join(os.path.dirname(__file__), "test_watch_folder")
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
REPORT_DIR = os.path.join(os.path.dirname(__file__), "reports")

SYSTEM_LOG_FILE = os.path.join(LOG_DIR, "system_metrics.csv")
DIRECTORY_LOG_FILE = os.path.join(LOG_DIR, "directory_changes.csv")

def main():
    print("==========================================")
    print("   AAC6164 LINUX MONITORING SYSTEM")
    print("   Created by Group 6")
    print("==========================================")
    
    # 1. Setup Folders
    if not os.path.exists(WATCH_DIRECTORY):
        os.makedirs(WATCH_DIRECTORY)
        print(f"[INIT] Created watch folder: {WATCH_DIRECTORY}")
    
    # 2. Initialize Modules
    print("[INIT] Initializing modules...")
    dir_monitor = DirectoryMonitor(WATCH_DIRECTORY, DIRECTORY_LOG_FILE)
    sys_monitor = SystemMonitor(SYSTEM_LOG_FILE)
    reporter = ReportGenerator(SYSTEM_LOG_FILE, DIRECTORY_LOG_FILE, REPORT_DIR)
    
    print(f"[RUNNING] Monitoring started. Press Ctrl+C to stop.")
    print(f"[INFO] Data will be saved to: {LOG_DIR}")
    
    cycle_count = 0
    
    try:
        while True:
            # Run System Monitor (Student B)
            sys_monitor.log_metrics()
            
            # Run Directory Monitor (Student A)
            dir_monitor.check_updates()
            
            # Every 6 cycles (approx 1 minute), generate the visual report
            if cycle_count > 0 and cycle_count % 6 == 0:
                reporter.generate_full_report()
            
            cycle_count += 1
            # Wait 10 seconds before next check [cite: 42]
            time.sleep(10)

    except KeyboardInterrupt:
        print("\n\n[STOP] Monitoring stopped by user.")
        print("[FINAL] Generating final report...")
        reporter.generate_full_report()
        print("Goodbye.")

if __name__ == "__main__":
    main()
