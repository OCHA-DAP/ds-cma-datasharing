# CMME Seasonal Forecast History — Zarr Access

Monthly mean precipitation forecasts from the CMA CMME model, 1991–2020.

**Blob path:** `projects/ds-cma-datasharing/processed/CMME_history.zarr`
**Account:** `imb0chd0dev` (dev stage)

## Dataset structure

| Dimension   | Size | Description                              |
|-------------|------|------------------------------------------|
| `init_time` | 360  | Initialization month (1991-01 to 2020-12)|
| `lead`      | 6    | Lead time in months ahead (1–6)          |
| `lat`       | 181  | Latitude 90°N to 90°S, 1° resolution    |
| `lon`       | 360  | Longitude 0°–359°E, 1° resolution       |

**Variable:** `PREC` — monthly mean precipitation (mm/day)
**CRS:** EPSG:4326

## Opening the dataset

This store uses **zarr v3 format** (`zarr.json` metadata, not `.zmetadata`). Two things follow from that:

- Use `zarr.storage.FsspecStore` instead of `fs.get_mapper()` — the latter returns a zarr v2-style mapper that zarr v3 doesn't read correctly.
- Pass `consolidated=False` to `xr.open_zarr` — zarr v3 stores don't have consolidated metadata, so xarray must read each array's metadata individually.

```python
import os
import adlfs
import xarray as xr
import zarr

fs = adlfs.AzureBlobFileSystem(
    account_name="imb0chd0dev",
    sas_token=os.environ["DSCI_AZ_BLOB_DEV_SAS_WRITE"],
)
store = zarr.storage.FsspecStore(
    fs, path="projects/ds-cma-datasharing/processed/CMME_history.zarr"
)
ds = xr.open_zarr(store, consolidated=False)  # lazy — nothing loaded until .compute()
```

## Example queries

```python
# All forecasts initialized in June, at 1-month lead
june_inits = ds.sel(lead=1).isel(init_time=ds.init_time.dt.month.values == 6)

# A specific initialization month (June 2010), all lead times
ds.sel(init_time="2010-06")["PREC"]

# Long-term mean by lead time (load into memory)
ds["PREC"].mean("init_time").compute()

# Single year
ds.sel(init_time=slice("2005-01", "2005-12"))
```

## Clipping to a geometry

```python
import rioxarray  # registers .rio accessor

# geometries: list of shapely geometries or a GeoDataFrame's .geometry
ds_spatial = ds.rio.set_spatial_dims(x_dim="lon", y_dim="lat").rio.write_crs("EPSG:4326")
ds_clipped = ds_spatial.rio.clip(geometries)
```

Note: `rio.clip` loads the spatial data for matching chunks into memory. To minimize
data fetched, select `init_time` / `lead` slices before clipping.

```python
# Efficient: filter time first, then clip
subset = ds.sel(lead=1, init_time=slice("2000-01", "2010-12"))
ds_clipped = subset.rio.set_spatial_dims(x_dim="lon", y_dim="lat") \
                   .rio.write_crs("EPSG:4326") \
                   .rio.clip(geometries)
result = ds_clipped["PREC"].compute()
```

## Dependencies

```
adlfs
xarray
zarr>=3
rioxarray
dask
```
