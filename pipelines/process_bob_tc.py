"""
Parse CMA BABJ diamond-7 TC forecast files from blob storage and write a
tidy parquet to {PROJECT_PREFIX}/processed/2022-2025_BoB_TC.parquet.

Source blobs: {PROJECT_PREFIX}/cma_ftp/data_out/2022-2025_BoB_TC/**/*.dat
Output blob:  {PROJECT_PREFIX}/processed/2022-2025_BoB_TC.parquet
"""

import ocha_stratus as stratus

from src.constants import PROJECT_PREFIX
from src.datasources.cma_cyclones import load_bob_tc_forecasts

BLOB_PREFIX = f"{PROJECT_PREFIX}/cma_ftp/data_out/2022-2025_BoB_TC"
OUTPUT_BLOB = f"{PROJECT_PREFIX}/processed/2022-2025_BoB_TC.parquet"


def main():
    combined = load_bob_tc_forecasts(BLOB_PREFIX)
    combined = combined.sort_values(
        ["storm_id", "analysis_datetime", "forecast_hour"]
    ).reset_index(drop=True)

    print(f"\nTotal rows: {len(combined)}")
    print(combined.dtypes)
    print(combined.head())

    print(f"\nUploading to {OUTPUT_BLOB} ...")
    stratus.upload_parquet_to_blob(combined, OUTPUT_BLOB)
    print("Done.")


if __name__ == "__main__":
    main()
