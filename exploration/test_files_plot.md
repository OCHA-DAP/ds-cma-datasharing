---
jupyter:
  jupytext:
    formats: ipynb,md
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.1
  kernelspec:
    display_name: ds-cma-datasharing
    language: python
    name: ds-cma-datasharing
---

# Check test files

Checking test files from SFTP

```python
%load_ext jupyter_black
%load_ext autoreload
%autoreload 2
```

```python
import ocha_stratus as stratus
import xarray as xr

from src.constants import *
```

```python
blob_name = (
    f"{PROJECT_PREFIX}/cma_ftp/data_out/cmme/PREC.6m.CMME.202508.1x1.ens.nc"
)
```

```python
data = stratus.load_blob_data(blob_name)
```

```python
ds = xr.open_dataset(data, decode_times=False)
```

```python
da_plot = ds.isel(time=0)["PREC"]
```

```python
da_plot.where(da_plot >= 0).plot()
```
