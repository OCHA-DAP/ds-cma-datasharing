"""
Convert CMME seasonal forecast history archive from blob storage to a zarr
dataset at ds-cma-datasharing/processed/CMME_history.zarr.

Source: ds-cma-datasharing/cma_ftp/data_out/CMME_History/CMME_history.zip
Output: ds-cma-datasharing/processed/CMME_history.zarr

Data: Monthly mean precipitation forecasts (mm/day), 199101–202012.
      One .nc file per initialization month with 6 monthly lead times.

Output dimensions: (init_time=360, lead=6, lat=181, lon=360)
  - init_time: initialization month (datetime64, monthly 1991-01 to 2020-12)
  - lead: lead time in months ahead (1–6)
  - lat, lon: 1°×1° global grid

Usage:
    import adlfs, os, zarr, xarray as xr

    fs = adlfs.AzureBlobFileSystem(
        account_name="imb0chd0dev",
        sas_token=os.environ["DSCI_AZ_BLOB_DEV_SAS_WRITE"],
    )
    store = zarr.storage.FsspecStore(
        fs, path="projects/ds-cma-datasharing/processed/CMME_history.zarr"
    )
    # lazy — nothing loaded until .compute()
    ds = xr.open_zarr(store, consolidated=False)

    # All June initializations at lead 1:
    ds.sel(lead=1).isel(
        init_time=ds.init_time.dt.month.values == 6
    )["PREC"]

    # Clip to geometry (shapely or GeoDataFrame geometries):
    skip = ("init_time", "lead", "lat")
    x_dim = [d for d in ds["PREC"].dims if d not in skip][0]
    y_dim = [d for d in ds["PREC"].dims if d not in (*skip, x_dim)][0]
    ds_clipped = ds.rio.set_spatial_dims(
        x_dim=x_dim, y_dim=y_dim
    ).rio.write_crs("EPSG:4326").rio.clip(geometries)
"""

import io
import os
import re
import zipfile

import adlfs
import numpy as np
import ocha_stratus as stratus
import pandas as pd
import rioxarray  # noqa: F401 — registers .rio accessor
import xarray as xr
import zarr

ACCOUNT_NAME = "imb0chd0dev"
SAS_TOKEN_ENV = "DSCI_AZ_BLOB_DEV_SAS_WRITE"
CONTAINER = "projects"
MISSING_VALUE = -1.0e10

INPUT_BLOB = (
    "ds-cma-datasharing/cma_ftp/data_out/CMME_History/CMME_history.zip"
)
OUTPUT_PATH = "ds-cma-datasharing/processed/CMME_history.zarr"

_NC_PATTERN = re.compile(r"PREC\.6m\.CMME\.(\d{6})\.1x1\.ens\.nc$")


def _parse_init_time(filename: str) -> pd.Timestamp:
    m = _NC_PATTERN.search(filename)
    if not m:
        raise ValueError(f"Unexpected filename: {filename}")
    yyyymm = m.group(1)
    return pd.Timestamp(year=int(yyyymm[:4]), month=int(yyyymm[4:]), day=1)


def _load_nc(zf: zipfile.ZipFile, name: str) -> xr.Dataset:
    ds = xr.open_dataset(
        io.BytesIO(zf.read(name)), decode_times=False, engine="scipy"
    )
    prec = ds["PREC"]
    # Replace CMA missing value (-1e10) with NaN
    prec = prec.where(prec > MISSING_VALUE / 10)
    # Identify dims by size: 181=lat, 360=lon, remainder=lead
    lat_dim = next(d for d in prec.dims if prec.sizes[d] == 181)
    lon_dim = next(d for d in prec.dims if prec.sizes[d] == 360)
    time_dim = next(d for d in prec.dims if d not in (lat_dim, lon_dim))
    n_lead = prec.sizes[time_dim]
    prec = (
        prec.assign_coords({time_dim: np.arange(1, n_lead + 1)})
        .rename({time_dim: "lead", lat_dim: "lat", lon_dim: "lon"})
        .assign_coords(
            lat=np.linspace(90, -90, 181),
            lon=np.arange(0, 360, dtype=float),
        )
    )
    prec.attrs["units"] = "mm/day"
    prec.attrs["long_name"] = "Monthly mean precipitation"
    return prec.to_dataset()


def main():
    print(f"Loading {INPUT_BLOB} ...")
    zip_bytes = stratus.load_blob_data(INPUT_BLOB)

    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        all_names = zf.namelist()
        nc_names = sorted(n for n in all_names if _NC_PATTERN.search(n))
        print(f"Found {len(nc_names)} matching .nc files in zip")

        if not nc_names:
            print("Zip contents (first 20):")
            for n in all_names[:20]:
                print(f"  {n}")
            raise SystemExit(
                "No matching .nc files found — check zip structure"
            )

        datasets = []
        init_times = []
        for i, name in enumerate(nc_names, 1):
            init_time = _parse_init_time(name)
            print(f"  [{i}/{len(nc_names)}] {name} → {init_time:%Y-%m}")
            datasets.append(_load_nc(zf, name))
            init_times.append(init_time)

    print("Concatenating ...")
    combined = xr.concat(
        datasets,
        dim=pd.DatetimeIndex(init_times, name="init_time"),
    )
    combined.attrs["source"] = "CMA CMME seasonal forecast (199101–202012)"

    print(f"\n{combined}\n")
    print(f"Writing to {OUTPUT_PATH} ...")
    sas_token = os.environ[SAS_TOKEN_ENV]
    fs = adlfs.AzureBlobFileSystem(
        account_name=ACCOUNT_NAME,
        sas_token=sas_token.lstrip("?"),
    )
    store = zarr.storage.FsspecStore(fs, path=f"{CONTAINER}/{OUTPUT_PATH}")
    chunked = combined.chunk(
        {"init_time": 12, "lead": 6, "lat": 181, "lon": 360}
    )

    print("Writing zarr ...")
    chunked.to_zarr(store, consolidated=False, mode="w")

    print("Consolidating metadata ...")
    zarr.consolidate_metadata(store)
    print("Done.")


if __name__ == "__main__":
    main()
