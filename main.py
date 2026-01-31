import time
import os
from modules.monitor_directory import DirectoryMonitor
from modules.monitor_system import SystemMonitor
from modules.reports_generator import ReportGenerator

# CONFIGURATION
WATCH_DIR = "./test_watch_folder"
LOG_DIR = "./logs"
REPORT_DIR = "./reports"
SYS_LOG = os.path.join(LOG_DIR, "system_metrics.csv")
DIR_LOG = os.path.join(LOG_DIR, "directory_changes.csv")

def main():
    print("=== STARTING AAC6164 LINUX MONITOR ===")
    
    # 1. Initialize Modules
    dir_mon = DirectoryMonitor(WATCH_DIR, DIR_LOG)
    sys_mon = SystemMonitor(SYS_LOG)
    reporter = ReportGenerator(SYS_LOG, DIR_LOG, REPORT_DIR)

    # 2. Main Loop (Runs every 10 seconds)
    try:
        loop_count = 0
        while True:
            print(f"\n--- Scan Cycle {loop_count} ---")
            
            # Run Individual Components
            dir_mon.scan()       # Student A's Code
            sys_mon.log_metrics() # Student B's Code
            
            # Every 6 cycles (1 minute), update the reports/charts
            if loop_count % 6 == 0 and loop_count > 0:
                print("Generating Reports...")
                reporter.generate_charts() # Student C's Code
            
            loop_count += 1
            time.sleep(10) # Requirement: Periodic monitoring [cite: 42]
            
    except KeyboardInterrupt:
        print("\nStopping Monitor...")

if __name__ == "__main__":
    # Create necessary folders first
    if not os.path.exists(WATCH_DIR): os.makedirs(WATCH_DIR)
    if not os.path.exists(LOG_DIR): os.makedirs(LOG_DIR)
    
    main()
