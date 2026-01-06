import pandas as pd
import datetime as dt
from openpyxl import workbook, load_workbook


#read all the input files
raw_Mail_file = pd.read_csv(r"C:\Python-Workspace\Projects\Project02_5G_ZeroTraffic\MDP_Portal_5G_Zero_Traffic_Cell_Backup_2025101411.csv",encoding='utf-8', low_memory=False, dtype=str)
online_Sheet = pd.read_excel(r"C:\Python-Workspace\Projects\Project02_5G_ZeroTraffic\5G_Zerotraffic_Trending_18092025.xlsx", dtype=str, sheet_name="Consol_Non-Consol")
MDP_File_Availablity = pd.read_csv(r"C:\Python-Workspace\Projects\Project02_5G_ZeroTraffic\ESVXXXI_TH_ESVXXXI_5G_Downtime_Man_Auto_20251016174242_WO_227681258.csv",dtype=str)
Engineer_Maping = pd.read_excel(r"C:\Python-Workspace\Projects\Project02_5G_ZeroTraffic\NEWOWNERNAMES_16July2024.xlsx",sheet_name="NR Owners", dtype=str)


#creating output file dataframe
output_file = pd.DataFrame()

#Initial filtering
raw_Mail_file["No_of_Hours"]= pd.to_numeric(raw_Mail_file["No_of_Hours"],errors='coerce')
raw_Mail_file["NR_Traffic"]= pd.to_numeric(raw_Mail_file["NR_Traffic"],errors='coerce')
raw_Mail_file["Datex"]= pd.to_datetime(raw_Mail_file["Datex"],errors='coerce', dayfirst=True)
filtered_as_per_needed = raw_Mail_file[(raw_Mail_file["Datex"]==raw_Mail_file["Datex"].max()) &(raw_Mail_file["No_of_Hours"]==4)& (raw_Mail_file["NR_Traffic"]==0)&(raw_Mail_file["administrativeState"]=="UNLOCKED")&(raw_Mail_file["operationalState"]=="ENABLED")]

#convert to date format
filtered_as_per_needed.loc[:,"Datex"]= pd.to_datetime(filtered_as_per_needed["Datex"],errors="coerce", dayfirst=True).dt.date

online_Sheet["Date"] = pd.to_datetime(online_Sheet["Date"],errors="coerce", dayfirst=True).dt.date

print(filtered_as_per_needed)

#insert all the required columns in output_file 
output_file["Operator"] = filtered_as_per_needed["Operator"]
output_file["Date"]= filtered_as_per_needed["Datex"]
output_file["Sitename"]= filtered_as_per_needed["Sitename"]
output_file["UPC"]= filtered_as_per_needed["UPC"]
output_file["Region"]= filtered_as_per_needed["Region"]
output_file["Enodeb"]= filtered_as_per_needed["Gnodeb"]
output_file["Cell_Name"]= filtered_as_per_needed["NR_Cell_Name"]
#first 3 letters of Sitename as Province
output_file["Province"]= filtered_as_per_needed["Sitename"].str[:3]
output_file["NR_Traffic"]= filtered_as_per_needed["NR_Traffic"].astype(int)

output_file["Availability"]= pd.merge(output_file,MDP_File_Availablity[["NR_Cell_name","Radio_Availablity(%)"]],left_on="Cell_Name",right_on="NR_Cell_name",how="left")["Radio_Availablity(%)"]
output_file["Availability"]=pd.to_numeric(output_file["Availability"],errors="coerce")
output_file["Consol / Legacy"]= filtered_as_per_needed["ONAIR_Status"]
output_file["syncStatus"]= filtered_as_per_needed["syncStatus"]
output_file["administrativeState"]= filtered_as_per_needed["administrativeState"]
output_file["operationalState"] =filtered_as_per_needed["operationalState"]
output_file["Engineer Name"] = pd.merge(output_file,Engineer_Maping[["Provience/ Region","New Owner"]], left_on="Province", right_on="Provience/ Region", how="left")["New Owner"].fillna("")

output_file["Remarks from Automation"]= filtered_as_per_needed["Remarks"]

#now append it to online_Sheet

merged_data = pd.concat([online_Sheet, output_file], ignore_index=True)

#replace unnecessary UPC values with valid like UPC-1, UPC-2 etc
merged_data["UPC"] = merged_data["UPC"].replace({
    "UPC_1_Upper_North": "UPC-1",
    "UPC_2_Lower_North": "UPC-2",
    "UPC_6_Central": "UPC-6"
})

#replace non-Consolidated with Legacy
merged_data["Consol / Legacy"] = merged_data["Consol / Legacy"].replace({
    "Non-Consolidated": "Legacy"
})


merged_data_consolidated = merged_data[merged_data["Consol / Legacy"]=="Consolidated"]

print(merged_data_consolidated)

merged_data_consolidated["Date"] = pd.to_datetime(merged_data_consolidated["Date"])
merged_data_consolidated["Date"] = merged_data_consolidated["Date"].dt.date

summary = pd.crosstab(index=merged_data_consolidated["UPC"], columns=merged_data_consolidated["Date"], values=merged_data_consolidated["Cell_Name"], aggfunc="count", margins=True, margins_name="Grand Total")
print(summary)

No_of_Days_ZeroTraffic = pd.crosstab(index=merged_data_consolidated["Cell_Name"], columns=merged_data_consolidated["Date"], values=merged_data_consolidated["Cell_Name"], aggfunc="count", margins=True, margins_name="Grand Total")

# Reset index so 'Cell_Name' becomes a column (needed for merging)
No_of_Days_ZeroTraffic = No_of_Days_ZeroTraffic.reset_index()

# Merge required columns to get Consol / Legacy, UPC, Province
No_of_Days_ZeroTraffic = No_of_Days_ZeroTraffic.merge(
    merged_data_consolidated[["Cell_Name", "Consol / Legacy", "UPC", "Province"]].drop_duplicates(),
    on="Cell_Name",
    how="left"
)
# Reorder columns to bring the metadata columns (Consol / Legacy, UPC, Province) after Cell_Name
cols = list(No_of_Days_ZeroTraffic.columns)

# Example: ['Cell_Name', 'Consol / Legacy', 'UPC', 'Province', '2025-10-01', '2025-10-02', ..., 'Grand Total']
new_order = ["Cell_Name", "Consol / Legacy", "UPC", "Province"] + [col for col in cols if col not in ["Cell_Name", "Consol / Legacy", "UPC", "Province"]]
No_of_Days_ZeroTraffic = No_of_Days_ZeroTraffic[new_order]
No_of_Days_ZeroTraffic= No_of_Days_ZeroTraffic.sort_values("Grand Total", ascending=False)
print(No_of_Days_ZeroTraffic)

#Save the file

import os

output_path = r"C:\Python-Workspace\Projects\Project02_5G_ZeroTraffic\output.xlsx"

# Check if the file exists
if os.path.exists(output_path):
    # If file exists, replace the target sheet
    with pd.ExcelWriter(output_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        merged_data.to_excel(writer, sheet_name="Consol_Non-Consol", index=False)
        summary.to_excel(writer, sheet_name="Summary", index=True)
        No_of_Days_ZeroTraffic.to_excel(writer, sheet_name="No. Of Days ZeroTraffic", index=False)
else:
    # If file doesn't exist, create it from scratch
    with pd.ExcelWriter(output_path, engine='openpyxl', mode='w') as writer:
        merged_data.to_excel(writer, sheet_name="Consol_Non-Consol", index=False)
        summary.to_excel(writer, sheet_name="Summary", index=False)
        No_of_Days_ZeroTraffic.to_excel(writer, sheet_name="No. Of Days ZeroTraffic", index=False)

print(f"✅ Output saved successfully at: {output_path}")