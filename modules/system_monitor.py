import psutil
import time
import os
from datetime import datetime

def get_system_metrics():
    # 1. CPU Metrics
    cpu_usage = psutil.cpu_percent(interval=1)
    load_1, load_5, load_15 = psutil.getloadavg()
    total_processes = len(psutil.pids())

    # 2. Memory Metrics
    mem = psutil.virtual_memory()
    
    # 3. Disk Metrics (Root Partition)
    disk = psutil.disk_usage('/')

    # 4. System Uptime
    uptime_seconds = time.time() - psutil.boot_time()
    uptime_str = str(datetime.fromtimestamp(psutil.boot_time()))

    # 5. Active Processes Analysis
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

    # Sort for Top 3
    top_cpu = sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:3]
    top_mem = sorted(processes, key=lambda x: x['memory_percent'], reverse=True)[:3]

    # Print Report to Terminal
    print(f"\n--- System Report: {datetime.now()} ---")
    print(f"CPU Usage: {cpu_usage}% | Load: {load_1}, {load_5}, {load_15}")
    print(f"Processes: Total {total_processes} (Running: {running_count}, Sleeping: {sleeping_count})")
    print(f"Memory: {mem.percent}% (Used: {mem.used // (1024**2)}MB / Total: {mem.total // (1024**2)}MB)")
    print(f"Disk: {disk.percent}% (Free: {disk.free // (1024**3)}GB)")
    
    print("\nTop 3 CPU Processes:")
    for p in top_cpu: print(f"  PID {p['pid']}: {p['name']} ({p['cpu_percent']}%)")
    
    print("\nTop 3 Memory Processes:")
    for p in top_mem: print(f"  PID {p['pid']}: {p['name']} ({p['memory_percent']:.1f}%)")

if __name__ == "__main__":
    print("Starting System Monitor (Press Ctrl+C to stop)...")
    try:
        while True:
            get_system_metrics()
            time.sleep(10) # Collect metrics every 10 seconds
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")
