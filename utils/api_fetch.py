import pandas as pd
import requests

BASE = "https://data.epa.gov/dmapservice/ghg."
TABLES = [
    "pub_dim_facility",
    "hh_landfill_info",
    "hh_gas_collection_system_detls",
    "hh_lndfil_wthout_gas_clct_emis",
    "hh_hist_yr_waste_qty_detl"
]

def fetch_epa_table(table_name: str, start=1, end=10000):
    url = f"https://data.epa.gov/dmapservice/ghg.{table_name}/{start}:{end}/json"
    try:
        res = requests.get(url)
        res.raise_for_status()
        data = res.json()

        # Handle top-level list
        if isinstance(data, list):
            return pd.DataFrame(data)

        # Flatten nested structure
        for value in data.values():
            if isinstance(value, list):
                return pd.DataFrame(value)

        return pd.DataFrame()
    except Exception as e:
        print(f"Error fetching {table_name}: {e}")
        return pd.DataFrame()

def fetch_and_merge_hh_tables():
    main = fetch_epa_table("pub_dim_facility")
    if main.empty:
        print("No data from pub_dim_facility")
        return pd.DataFrame()

    landfill = fetch_epa_table("hh_landfill_info")
    gcs = fetch_epa_table("hh_gas_collection_system_detls")

    # Drop overlapping columns before merge to avoid _x/_y suffixes
    drop_cols = ["facility_name", "state", "city"]
    for df in [landfill, gcs]:
        for col in drop_cols:
            if col in df.columns:
                df.drop(columns=col, inplace=True)

    def safe_merge(main, df, on=["facility_id"]):
        if df.empty:
            return main
        df = df.groupby(on).agg(lambda x: '|'.join(map(str, x.dropna().unique()))).reset_index()
        return pd.merge(main, df, on=on, how='left')

    if not gcs.empty:
        main = safe_merge(main, gcs)

    if not landfill.empty:
        main = safe_merge(main, landfill)

    return main
