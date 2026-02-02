import time
# intergration test commit
import os
import sys

# Ensure Python can find the 'modules' folder
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from modules.monitor_directory import DirectoryMonitor
from modules.monitor_system import SystemMonitor
from modules.reports_generator import ReportGenerator

# --- CONFIGURATION ---
WATCH_DIRECTORY = os.path.join(os.path.dirname(__file__), "test_watch_folder")
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
REPORT_DIR = os.path.join(os.path.dirname(__file__), "reports")
SYSTEM_LOG_FILE = os.path.join(LOG_DIR, "system_metrics.csv")
DIRECTORY_LOG_FILE = os.path.join(LOG_DIR, "directory_changes.csv")

def main():
    print("==========================================")
    print("   AAC6164 LINUX MONITORING SYSTEM")
    print("   Made with <3 by Group 6")
    print("   Initializing...")
    print("==========================================")
    
    # 1. Setup Folders
    if not os.path.exists(WATCH_DIRECTORY): os.makedirs(WATCH_DIRECTORY)
    if not os.path.exists(LOG_DIR): os.makedirs(LOG_DIR)
    
    # 2. Initialize Modules
    dir_monitor = DirectoryMonitor(WATCH_DIRECTORY, DIRECTORY_LOG_FILE)
    sys_monitor = SystemMonitor(SYSTEM_LOG_FILE)
    reporter = ReportGenerator(SYSTEM_LOG_FILE, DIRECTORY_LOG_FILE, REPORT_DIR)
    
    cycle_count = 0
    
    try:
        while True:
            # Run System Monitor (Prints the big UI block)
            sys_monitor.log_metrics()
            
            # Run Directory Monitor (Only prints if files change)
            dir_monitor.check_updates()
            
            # Visual Reports (Every 1 minute / 6 cycles)
            if cycle_count > 0 and cycle_count % 6 == 0:
                reporter.generate_full_report()
            
            cycle_count += 1
            time.sleep(10)

    except KeyboardInterrupt:
        print("\n\n[STOP] Monitoring stopped.")
        print("[FINAL] Generating final report...")
        reporter.generate_full_report()

if __name__ == "__main__":
    main()
