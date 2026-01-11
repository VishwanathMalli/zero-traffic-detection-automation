import os
import json
import pandas as pd

# This SQL setup is for local automation and reporting.
# The script creates a database (if not exists) and stores
# processed zero-traffic KPI data for further analysis.


#--------------SQL setup------------------------------------
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

db_user = "root"
db_password = quote_plus("Vishwa@0546")   # URL-encoded
db_host = "localhost"
db_port = 3306
db_name = "4G5G_Zerotraffic_Automation"

# Engine WITHOUT database
engine_server = create_engine(
    f"mysql+mysqlconnector://{db_user}:{db_password}"
    f"@{db_host}:{db_port}",
    echo=False
)
#Create database if not exists
with engine_server.begin() as conn:
    conn.execute(
        text(f"CREATE DATABASE IF NOT EXISTS {db_name}")
    )

#Create engine WITH database
engine_db = create_engine(
    f"mysql+mysqlconnector://{db_user}:{db_password}"
    f"@{db_host}:{db_port}/{db_name}",
    echo=False
)

#----------------------------------SQL setup ended------------------------------------



# =========================================================
# CONFIG LOADER
# =========================================================

def load_config(config_path=r"C:\Users\esvxxxi\Downloads\Trying_with_sql\config.json"):
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except Exception as e:
        raise RuntimeError(f"Failed to load config file: {e}")

# =========================================================
# FILE READERS
# =========================================================

def read_csv_file(path, **kwargs):
    try:
        return pd.read_csv(path, **kwargs)
    except FileNotFoundError:
        raise FileNotFoundError(f"CSV file not found: {path}")
    except Exception as e:
        raise RuntimeError(f"Error reading CSV file {path}: {e}")

def read_excel_file(path, **kwargs):
    try:
        return pd.read_excel(path, **kwargs)
    except FileNotFoundError:
        raise FileNotFoundError(f"Excel file not found: {path}")
    except Exception as e:
        raise RuntimeError(f"Error reading Excel file {path}: {e}")

# =========================================================
# CORE PROCESSING FUNCTIONS
# =========================================================

def filter_zero_traffic_cells(raw_df):
    raw_df["No_of_Hours"] = pd.to_numeric(raw_df["No_of_Hours"], errors="coerce")
    raw_df["NR_Traffic"] = pd.to_numeric(raw_df["NR_Traffic"], errors="coerce")
    raw_df["Datex"] = pd.to_datetime(raw_df["Datex"], errors="coerce", dayfirst=True)

    latest_date = raw_df["Datex"].max()

    filtered = raw_df[
        (raw_df["Datex"] == latest_date) &
        (raw_df["No_of_Hours"] == 4) &
        (raw_df["NR_Traffic"] == 0) &
        (raw_df["administrativeState"] == "UNLOCKED") &
        (raw_df["operationalState"] == "ENABLED")
    ].copy()

    filtered["Datex"] = filtered["Datex"].dt.date
    return filtered

def build_output_dataframe(filtered_df):
    return pd.DataFrame({
        "Operator": filtered_df["Operator"],
        "Date": filtered_df["Datex"],
        "Sitename": filtered_df["Sitename"],
        "UPC": filtered_df["UPC"],
        "Region": filtered_df["Region"],
        "Enodeb": filtered_df["Gnodeb"],
        "Cell_Name": filtered_df["NR_Cell_Name"],
        "Province": filtered_df["Sitename"].str[:3],
        "NR_Traffic": filtered_df["NR_Traffic"].astype(int),
        "Consol / Legacy": filtered_df["ONAIR_Status"],
        "syncStatus": filtered_df["syncStatus"],
        "administrativeState": filtered_df["administrativeState"],
        "operationalState": filtered_df["operationalState"],
        "Remarks from Automation": filtered_df["Remarks"]
    })

def enrich_with_availability(output_df, availability_df):
    output_df["Availability"] = (
        output_df.merge(
            availability_df[["NR_Cell_name", "Radio_Availablity(%)"]],
            left_on="Cell_Name",
            right_on="NR_Cell_name",
            how="left"
        )["Radio_Availablity(%)"]
    )
    output_df["Availability"] = pd.to_numeric(output_df["Availability"], errors="coerce")
    return output_df

def enrich_with_engineer(output_df, engineer_df):
    output_df["Engineer Name"] = (
        output_df.merge(
            engineer_df[["Provience/ Region", "New Owner"]],
            left_on="Province",
            right_on="Provience/ Region",
            how="left"
        )["New Owner"]
        .fillna("")
    )
    return output_df

# =========================================================
# SUMMARY GENERATION
# =========================================================

def generate_summary(merged_df):
    consolidated = merged_df[
        merged_df["Consol / Legacy"] == "Consolidated"
    ].copy()

    consolidated["Date"] = pd.to_datetime(consolidated["Date"]).dt.date

    summary = pd.crosstab(
        index=consolidated["UPC"],
        columns=consolidated["Date"],
        values=consolidated["Cell_Name"],
        aggfunc="count",
        margins=True,
        margins_name="Grand Total"
    )

    zero_days = pd.crosstab(
        index=consolidated["Cell_Name"],
        columns=consolidated["Date"],
        values=consolidated["Cell_Name"],
        aggfunc="count",
        margins=True,
        margins_name="Grand Total"
    ).reset_index()

    zero_days = zero_days.merge(
        consolidated[["Cell_Name", "Consol / Legacy", "UPC", "Province"]].drop_duplicates(),
        on="Cell_Name",
        how="left"
    )

    ordered_cols = (
        ["Cell_Name", "Consol / Legacy", "UPC", "Province"] +
        [c for c in zero_days.columns
         if c not in ["Cell_Name", "Consol / Legacy", "UPC", "Province"]]
    )

    return summary, zero_days[ordered_cols].sort_values("Grand Total", ascending=False)

# =========================================================
# MAIN
# =========================================================

def main():
    try:
        config = load_config()

        base_path = config["base_path"]

        raw_df = read_csv_file(
            os.path.join(base_path, config["raw_mail_file"]),
            encoding="utf-8", low_memory=False, dtype=str
        )

        online_df = read_excel_file(
            os.path.join(base_path, config["online_sheet_file"]),
            sheet_name=config["online_sheet_name"], dtype=str
        )

        availability_df = read_csv_file(
            os.path.join(base_path, config["availability_file"]),
            dtype=str
        )

        engineer_df = read_excel_file(
            os.path.join(base_path, config["engineer_mapping_file"]),
            sheet_name=config["engineer_mapping_sheet"], dtype=str
        )

        filtered_df = filter_zero_traffic_cells(raw_df)
        output_df = build_output_dataframe(filtered_df)
        output_df = enrich_with_availability(output_df, availability_df)
        output_df = enrich_with_engineer(output_df, engineer_df)

        merged_df = pd.concat([online_df, output_df], ignore_index=True)

        merged_df["UPC"] = merged_df["UPC"].replace({
            "UPC_1_Upper_North": "UPC-1",
            "UPC_2_Lower_North": "UPC-2",
            "UPC_6_Central": "UPC-6"
        })

        merged_df["Consol / Legacy"] = merged_df["Consol / Legacy"].replace({
            "Non-Consolidated": "Legacy"
        })

        summary_df, zero_days_df = generate_summary(merged_df)

        output_path = os.path.join(base_path, config["output_file"])
        mode = "a" if os.path.exists(output_path) else "w"



        # saving into MySQL database 
        merged_df.reset_index().to_sql(name="consol_non_consol", con=engine_db, if_exists="replace", index=False)
        summary_df.reset_index().to_sql(name="summary", con=engine_db, if_exists="replace")
        zero_days_df.reset_index().to_sql(name="no_of_days_zerotraffic", con=engine_db, if_exists="replace", index=False)





        with pd.ExcelWriter(
            output_path,
            engine="openpyxl",
            mode=mode,
            if_sheet_exists="replace"
        ) as writer:
            merged_df.to_excel(writer, sheet_name="Consol_Non-Consol", index=False)
            summary_df.to_excel(writer, sheet_name="Summary")
            zero_days_df.to_excel(writer, sheet_name="No. Of Days ZeroTraffic", index=False)


        print(f"✅ Output generated successfully: {output_path}")

    except Exception as e:
        print(f"❌ Script failed: {e}")

# =========================================================


if __name__ == "__main__":
    main()

