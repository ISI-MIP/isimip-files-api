Operations
==========

The following operations are available. Please note that some of the operations can be chained, e.g.

```
create_mask -> mask_mask -> compute_mean -> output_csv
```

Pleas also note the examples given in the [examples](../examples) directory.

### Select point

A time series of a point can be selected using:

```python
response = requests.post('https://files.isimip.org/api/v2', json={
    'paths': [...],
    'operations': [
        {
            'operation': 'select_point',
            'point': [52.380551, 13.064332]
        }
    ]
})
```

The operation is performed using [CDO](https://code.mpimet.mpg.de/projects/cdo) using:

```bash
cdo -f nc4c -z zip_5 -L -sellonlatbox,WEST,EAST,SOUTH,NORTH IFILE OFILE
```

### Select bounding box

A rectangular bounding box can be selected using:

```python
response = requests.post('https://files.isimip.org/api/v2', json={
    'paths': [...],
    'operations': [
        {
            'operation': 'select_bbox',
            'bbox': [-23.43651, 23.43651, -180, 180]
        }
    ]
})
```

The operation is performed using [CDO](https://code.mpimet.mpg.de/projects/cdo) using:

```bash
cdo -f nc4c -z zip_5 -L -selindexbox,IX,IX,IY,IY IFILE OFILE
```

where `IX` and `IY` are the grid indexes of the point computed from the file.

### Mask bounding box

A rectangular bounding box can be masked (everything outside is set to `missing_value`) using:

```python
response = requests.post('https://files.isimip.org/api/v2', json={
    'paths': [...],
    'operations': [
        {
            'operation': 'mask_bbox',
            'bbox': [-23.43651, 23.43651, -180, 180]
        }
    ]
})
```

The operation is performed using [CDO](https://code.mpimet.mpg.de/projects/cdo) using:

```bash
cdo -f nc4c -z zip_5 -L -sellonlatbox,WEST,EAST,SOUTH,NORTH IFILE OFILE
```

### Mask country

A country can be masked (everything outside is set to `missing_value`) using:

```python
response = requests.post('https://files.isimip.org/api/v2', json={
    'paths': [...],
    'operations': [
        {
            'operation': 'mask_country',
            'country': "bra"  # e.g. Brasil
        }
    ]
})
```

The operation is performed using [CDO](https://code.mpimet.mpg.de/projects/cdo) using:

```bash
cdo -f nc4c -z zip_5 -L -ifthen -selname,m_BRA COUNTRYMASK IFILE OFILE
```

### Mask land only

The landmass (without antarctica) can be masked (everything outside is set to `missing_value`) using:

```python
response = requests.post('https://files.isimip.org/api/v2', json={
    'paths': [...],
    'operations': [
        {
            'operation': 'mask_landonly'
        }
    ]
})
```

The operation is performed using [CDO](https://code.mpimet.mpg.de/projects/cdo) using:

```bash
cdo -f nc4c -z zip_5 -L -ifthen LANDSEAMASK IFILE OFILE
```

### Mask using a NetCDF mask

In order to mask using a custom NetCDF file, the file needs to be uploaded together with the JSON. This is done using the content type `multipart/form-data`. Using `requests` this is done slightly different as before:

```python
import json
from pathlib import Path

import requests

mask_path = Path('path/to/mask.nc')

data = {
    'paths': [...],
    'operations': [
        {
            'operation': 'mask_mask',
            'mask': 'mask.nc',
            'var': 'm_VAR'  # the mask variable in the NetCDF file
        }
    ]
}

response = requests.post(url, files={
    'data': json.dumps(data),
    'mask.nc': mask_path.read_bytes(),
})
```

The operation is performed using [CDO](https://code.mpimet.mpg.de/projects/cdo) using:

```bash
cdo -f nc4c -z zip_5 -L -ifthen -selname,m_VAR mask.nc IFILE OFILE
```

### Compute mean

After one of the [CDO](https://code.mpimet.mpg.de/projects/cdo) based operations (e.g. `mask_country`) a field mean can be computed using:

```python
response = requests.post('https://files.isimip.org/api/v2', json={
    'paths': [...],
    'operations': [
        {
            'operation': 'mask_country',
            'country': "bra"  # e.g. Brasil
        },
        {
            'operation': 'compute_mean'
        }
    ]
})
```

The operation is performed using [CDO](https://code.mpimet.mpg.de/projects/cdo) using:

```bash
cdo -f nc4c -z zip_5 -L -fldmean -ifthen -selname,m_BRA COUNTRYMASK IFILE OFILE
```

### Output CSV

After one of the other [CDO](https://code.mpimet.mpg.de/projects/cdo) based operations (e.g. `mask_country` and `compute_mean`) the output can be converted to [CSV](https://en.wikipedia.org/wiki/Comma-separated_values):

```python
response = requests.post('https://files.isimip.org/api/v2', json={
    'paths': [...],
    'operations': [
        {
            'operation': 'mask_country',
            'country': "bra"  # e.g. Brasil
        },
        {
            'operation': 'compute_mean'
        },
        {
            'operation': 'output_csv'
        }
    ]
})
```

The operation is performed using [CDO](https://code.mpimet.mpg.de/projects/cdo) using:

```bash
cdo -s outputtab,date,value,nohead -fldmean -ifthen -selname,m_BRA COUNTRYMASK IFILE OFILE
```

Afterwards the TAB seperated CDO output is converted to CSV.

Full examples are is given in [examples/time_series_bbox.py](../time_series_bbox.py) and [examples/time_series_country.py](../time_series_country.py).

### Cutout bounding box

Instead of using [CDO](https://code.mpimet.mpg.de/projects/cdo) to select a bounding box, the cut-out can also be performed using [ncks](https://nco.sourceforge.net/nco.html). This operation has a much better performance when applied to the high resolution data from [CHELSA-W5E5 v1.0: W5E5 v1.0 downscaled with CHELSA v2.0](https://doi.org/10.48364/ISIMIP.836809.3).

```python
response = requests.post('https://files.isimip.org/api/v2', json={
    'paths': [...],
    'operations': [
        {
            'operation': 'cutout_bbox',
            'bbox': [47.5520, 47.6680, 12.8719, 13.1393]
        }
    ]
})
```

The operation is performed using [ncks](https://nco.sourceforge.net/nco.html) using:

```bash
ncks -h -d lat,SOUTH,NORTH -d WEST,EAST IFILE OFILE
```

### Create mask

Mask can be created from vector based input file, namely [Shapefiles](https://en.wikipedia.org/wiki/Shapefile) or [GeoJSON files](https://en.wikipedia.org/wiki/GeoJSON). This operation is performed once and the resulting mask can then be used in the `mask_mask` operation. As for the `mask_mask` operation, the input file needs to be uploaded together with the JSON. This is done using the content type `multipart/form-data`. For a shapefile, the different files need to be in one zip file. Using `requests` this is done like this:

```python
import json
from pathlib import Path

import requests

shape_path = Path('path/to/shape.zip')

data = {
    'paths': [...],
    'operations': [
        {
            'operation': 'create_mask',
            'shape': 'shape.zip',
            'mask': 'shape.nc'
        },
        {
            'operation': 'mask_mask',
            'mask': 'shape.nc'
        }
    ]
}

response = requests.post(url, files={
    'data': json.dumps(data),
    'shape.zip': shape_path.read_bytes(),
})
```

Full examples are is given in [examples/time_series_shapefile.py](../time_series_shapefile.py) and [examples/time_series_geojson.py](../time_series_geojson.py).
