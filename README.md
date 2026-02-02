# Linux Monitoring System using Python.
AAC6164 Group Assignment: A Linux-based monitoring system using Python to track directory changes and system performance


# Report Generation Module (Student C)
This module is responsible for generating a system monitoring summary report based on log files collected from the system.

## How to run
Make sure you are in the project root directory, then run:

```bash
python3 modules/reports_generator.py

Input 
-CSV log files located in the logs/directory
-Example input file may include
   -CPU usage logs
   -Memory usage loss

Output
-A summary report generated at:
   reports/summary-reports.txt
-The report contains:
   -System usage summary
   -Information extracted from available log files

Description 
-Readd monitoring log data from the logs/directory
-Handles missing or empty og files safely
-Generates a readable summary report
-Display a success message after the report is generated