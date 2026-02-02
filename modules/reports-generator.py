import os 
import datetime

LOGS_DIR = "logs"
REPORTS_DIR = "reports"
SUMMARY_FILE = os.path.join(REPORTS_DIR, "summary-report.txt")


def generate_report():
    now = datetime.datetime.now()

    # Make sure reports folder exists
    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)

    with open(SUMMARY_FILE, "w") as f:
        f.write("System Monitoring Summary Report\n")
        f.write("--------------------------------\n")
        f.write(f"Generated at: {now}\n\n")

        if not os.path.exists(LOGS_DIR) or not os.listdir(LOGS_DIR):
            f.write("No log data available yet.\n")
        else:
            f.write("Log files detected:\n")    
            for file in os.listdir(LOGS_DIR):
                f.write(f"- {file}\n")

    print("Summary report generated successfully.")  


if __name__ == "__main__":
    generate_report()

            
