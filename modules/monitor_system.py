import psutil
import time
import csv
import os
from datetime import datetime, timedelta

class SystemMonitor:
    def __init__(self, log_file):
        self.log_file = log_file
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        # Initialize CSV with Headers
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Timestamp", 
                    "CPU_Usage_Pct", "Load_Avg_1min", 
                    "Total_Procs", "Running_Procs", "Sleeping_Procs",
                    "RAM_Used_Pct", "RAM_Available_MB",
                    "Disk_Used_Pct", "Disk_Total_GB", "Disk_Used_GB", "Disk_Free_GB", # Added Pct back
                    "System_Uptime_Sec", "System_Idle_Sec"
                ])

    def log_metrics(self):
        # --- 1. CPU Metrics ---
        cpu_usage = psutil.cpu_percent(interval=None)
        try:
            load_1, load_5, load_15 = os.getloadavg()
        except AttributeError:
            load_1, load_5, load_15 = 0, 0, 0
            
        # --- 2. Memory Metrics ---
        mem = psutil.virtual_memory()
        
        # --- 3. Disk Metrics ---
        disk = psutil.disk_usage('/')
        disk_total_gb = round(disk.total / (1024**3), 2)
        disk_used_gb = round(disk.used / (1024**3), 2)
        disk_free_gb = round(disk.free / (1024**3), 2)

        # --- 4. Uptime ---
        boot_time = psutil.boot_time()
        uptime_sec = time.time() - boot_time
        uptime_str = str(timedelta(seconds=int(uptime_sec)))
        idle_sec = psutil.cpu_times().idle
        idle_str = str(timedelta(seconds=int(idle_sec)))

        # --- 5. Active Processes ---
        processes = []
        running_count = 0
        sleeping_count = 0
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            try:
                pinfo = proc.info
                processes.append(pinfo)
                if pinfo['status'] == psutil.STATUS_RUNNING:
                    running_count += 1
                elif pinfo['status'] == psutil.STATUS_SLEEPING:
                    sleeping_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        total_processes = len(psutil.pids())
        top_cpu = sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:3]
        top_mem = sorted(processes, key=lambda x: x['memory_percent'], reverse=True)[:3]

        # --- CONSOLE OUTPUT ---
        print(f"\n--- System Report: {datetime.now().strftime('%H:%M:%S')} ---")
        print(f"Uptime: {uptime_str} | Idle: {idle_str}")
        print(f"CPU: {cpu_usage}% | Load: {load_1}, {load_5}, {load_15}")
        print(f"Procs: {total_processes} (Run: {running_count}, Sleep: {sleeping_count})")
        print(f"Mem: {mem.percent}% (Used: {mem.used // (1024**2)}MB)")
        print(f"Disk: {disk.percent}% (Total: {disk_total_gb}GB | Free: {disk_free_gb}GB)")
        
        print("\nTop 3 CPU Processes:")
        for p in top_cpu:
            print(f"  PID {p['pid']}: {p['name']} ({p['cpu_percent']}%)")
            
        print("\nTop 3 Memory Processes:")
        for p in top_mem:
            print(f"  PID {p['pid']}: {p['name']} ({p['memory_percent']:.1f}%)")

        # --- CSV LOGGING ---
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp,
                cpu_usage, load_1,
                total_processes, running_count, sleeping_count,
                mem.percent, round(mem.available / (1024**2), 2),
                disk.percent, disk_total_gb, disk_used_gb, disk_free_gb, # Included Pct + GBs
                int(uptime_sec), int(idle_sec)
            ])
