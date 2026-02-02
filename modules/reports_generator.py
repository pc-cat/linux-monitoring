import pandas as pd
import matplotlib.pyplot as plt
import os

class ReportGenerator:
    def __init__(self, sys_log, dir_log, output_dir):
        self.sys_log = sys_log
        self.dir_log = dir_log
        self.output_dir = output_dir
        
        # Create charts folder inside reports
        self.charts_dir = os.path.join(self.output_dir, "charts")
        os.makedirs(self.charts_dir, exist_ok=True)

    def generate_full_report(self):
        print("\n--- Generating Reports ---")
        self._generate_charts()
        self._generate_summary_text()
        print("--- Reports Generated in /reports folder ---\n")

    def _generate_charts(self):
        """Generates visual plots for CPU and Memory Usage"""
        try:
            if not os.path.exists(self.sys_log):
                return

            df = pd.read_csv(self.sys_log)
            if df.empty: return

            # Convert Timestamp to datetime objects for better plotting
            df['Timestamp'] = pd.to_datetime(df['Timestamp'])

            # Plot 1: CPU & RAM Trends
            plt.figure(figsize=(10, 6))
            plt.plot(df['Timestamp'], df['CPU_Usage_Pct'], label='CPU %', color='red')
            plt.plot(df['Timestamp'], df['RAM_Used_Pct'], label='RAM %', color='blue')
            plt.title('System Performance Trends')
            plt.xlabel('Time')
            plt.ylabel('Usage (%)')
            plt.legend()
            plt.grid(True)
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(os.path.join(self.charts_dir, "performance_trend.png"))
            plt.close()
            
            # Plot 2: Disk Usage Pie Chart
            plt.figure(figsize=(6, 4))
            latest = df.iloc[-1] # Get latest data point
            
            # Check if we have the right columns (Handle both Pct and GB versions)
            if 'Disk_Used_Pct' in df.columns:
                used_val = latest['Disk_Used_Pct']
                free_val = 100 - used_val
            else:
                # Fallback if Pct missing
                used_val = 50
                free_val = 50

            labels = ['Used', 'Free']
            sizes = [used_val, free_val]
            plt.pie(sizes, labels=labels, autopct='%1.1f%%', colors=['orange', 'green'])
            plt.title('Current Disk Usage')
            plt.savefig(os.path.join(self.charts_dir, "disk_usage.png"))
            plt.close()

        except Exception as e:
            print(f"[ERROR] Chart generation failed: {e}")

    def _generate_summary_text(self):
        """Generates the mandatory text/CSV summary report"""
        report_path = os.path.join(self.output_dir, "final_summary_report.txt")
        
        with open(report_path, "w") as f:
            f.write("AAC6164 GROUP ASSIGNMENT REPORT\n")
            f.write("===============================\n\n")
            
            # Section 1: Directory Statistics
            f.write("1. DIRECTORY MONITORING SUMMARY\n")
            f.write("-------------------------------\n")
            if os.path.exists(self.dir_log):
                try:
                    df_dir = pd.read_csv(self.dir_log)
                    if not df_dir.empty:
                        f.write(f"Total Events Recorded: {len(df_dir)}\n")
                        f.write(f"Files Created: {len(df_dir[df_dir['Event'] == 'CREATED'])}\n")
                        f.write(f"Files Deleted: {len(df_dir[df_dir['Event'] == 'DELETED'])}\n")
                        f.write(f"Files Modified: {len(df_dir[df_dir['Event'] == 'MODIFIED'])}\n")
                    else:
                        f.write("No events recorded yet.\n")
                except Exception as e:
                    f.write(f"Error reading directory log: {e}\n")
            else:
                f.write("Log file not found.\n")
            
            f.write("\n")

            # Section 2: System Statistics
            f.write("2. SYSTEM PERFORMANCE SUMMARY\n")
            f.write("-----------------------------\n")
            if os.path.exists(self.sys_log):
                try:
                    df_sys = pd.read_csv(self.sys_log)
                    if not df_sys.empty:
                        f.write(f"Average CPU Usage: {df_sys['CPU_Usage_Pct'].mean():.2f}%\n")
                        f.write(f"Average RAM Usage: {df_sys['RAM_Used_Pct'].mean():.2f}%\n")
                        # FIXED LINE BELOW: Changed 'Active_Processes' to 'Total_Procs'
                        f.write(f"Max Process Count: {df_sys['Total_Procs'].max()}\n")
                        
                        # Added Uptime Check
                        if 'System_Uptime_Sec' in df_sys.columns:
                             max_uptime = df_sys['System_Uptime_Sec'].max()
                             hours = int(max_uptime // 3600)
                             mins = int((max_uptime % 3600) // 60)
                             f.write(f"System Uptime: {hours}h {mins}m\n")
                    else:
                         f.write("Log file is empty.\n")
                except Exception as e:
                    # Now we print the actual error so you know WHY it failed
                    f.write(f"Error reading system data: {e}\n")
            else:
                f.write("Log file not found.\n")
