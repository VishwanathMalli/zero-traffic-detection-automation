# Zero Traffic Detection Automation (5G)

## Overview
This project automates zero-traffic cell detection for 5G networks using Python.
It processes daily KPI files, filters zero-traffic cells based on defined rules,
and generates consolidated Excel reports for network operations.

The automation replaces manual Excel-based analysis and ensures consistent,
repeatable reporting.

---

## Problem Statement
Manual identification of zero-traffic cells from large KPI datasets is time-consuming,
error-prone, and difficult to scale on a daily basis.
This automation streamlines the entire workflow from raw KPI input to final reports.

---

## Key Features
- Config-driven file handling using `config.json`
- Automated zero-traffic filtering logic
- Safe handling of invalid and missing KPI values
- Availability data enrichment
- Excel report generation with multiple sheets
- Built-in logging for traceability and debugging
- Modular and reusable Python functions

---

## Technologies Used
- Python
- Pandas
- openpyxl
- JSON
- Logging

---

## Project Structure
zero-traffic-detection-automation/
│
├── config.json
├── zero_traffic_automation.py
├── requirements.txt
├── README.md
│
├── input_samples/
│ ├── raw_kpi_sample.csv
│ ├── availability_sample.csv
│ └── trending_sample.xlsx
│
├── output_samples/
│ └── output.xlsx
│
└── zero_traffic_automation.log


---

## Configuration
All file paths and runtime settings are controlled through `config.json`.

Example:
{
"base_path": "C:/Python-Workspace/Projects/Project02_5G_ZeroTraffic",
"raw_mail_file": "raw_kpi.csv",
"online_sheet_file": "trending.xlsx",
"online_sheet_name": "Consol_Non-Consol",
"availability_file": "availability.csv",
"output_file": "output.xlsx",
"log_file": "zero_traffic_automation.log"
}


---

## How to Run
1. Clone the repository
2. Install dependencies:
pip install -r requirements.txt
3. Update file paths in `config.json`
4. Run the script:


---

## Output
The script generates an Excel file with the following sheets:
- Consol_Non-Consol – Detailed zero-traffic cell list
- Summary – Date-wise and UPC-wise summary
- No. Of Days ZeroTraffic – Cell-wise zero-traffic duration

---

## Zero-Traffic Logic
A cell is classified as zero-traffic if:
- Latest available date
- No_of_Hours equals 4
- NR_Traffic equals 0
- administrativeState is UNLOCKED
- operationalState is ENABLED

---

## Logging
All execution steps and errors are logged in:
zero_traffic_automation.log



This helps in debugging, auditing, and operational monitoring.

---

## Impact
- Manual effort reduced from hours to minutes
- Improved reporting accuracy and consistency
- Reusable automation for daily network operations

---

## Note
All input and output files used in this repository are sample or dummy data.
No production or customer data is included.

---

## Author
Vishwanath Malli  
Python Automation | Telecom Network Operations



