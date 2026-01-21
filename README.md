# Zero Traffic Detection Automation (LTE / NR)

## Overview
This project automates zero-traffic detection for LTE/NR cells using Python.  
It processes daily KPI data, applies business rules to identify zero-traffic cells, generates summary reports, and stores the processed results in both Excel and MySQL for further analysis.

---

## Key Features
- Automated detection of zero-traffic NR cells
- Business-rule based filtering using traffic hours, traffic volume, and cell state
- Consolidation of online and newly detected zero-traffic cells
- Summary and historical zero-traffic analysis
- Excel report generation
- MySQL database storage using SQLAlchemy

---

## Technologies Used
- Python
- Pandas
- SQLAlchemy
- MySQL
- Excel (openpyxl)

---

## Input Files
Configured through `config.json`:
- Raw NR KPI CSV file
- Online cells Excel file
- Engineer / province mapping Excel file

- please access the input files from drive link attached
  https://drive.google.com/drive/folders/1Y4I8nlI1w8makIy5cD4ootJW68-cD3cZ?usp=sharing

---

## Processing Logic
1. Load raw KPI and reference data
2. Convert numeric and date fields
3. Filter cells where:
   - Latest date
   - No_of_Hours = 4
   - NR_Traffic = 0
   - administrativeState = UNLOCKED
   - operationalState = ENABLED
4. Build structured output dataset
5. Enrich data with availability and engineer mapping
6. Merge with online cell data
7. Generate summary and zero-traffic day count

---

## SQL Integration
The automation stores processed KPI data into a MySQL database using SQLAlchemy.  
The database is created automatically for local usage.

### Tables Created
- consol_non_consol – consolidated zero-traffic and online cell data
- summary – UPC-wise zero-traffic summary
- no_of_days_zerotraffic – cell-wise zero-traffic day count

This allows reuse of processed data for reporting and analysis.

---

## Output
- Excel file with consolidated data, summary, and zero-traffic day count
- MySQL tables containing processed KPI results

---

## Configuration
All file paths and parameters are managed through `config.json`.

---

## How to Run
1. Update `config.json` with required paths
2. Ensure MySQL is running locally
3. Install required Python packages
4. Run the script:
```bash
python zero_traffic_automation.py


Use Case
Telecom network operations
Zero-traffic validation during site cutovers
Daily health check automation
Performance monitoring and KPI reporting


Author
Vishwanath Malli
