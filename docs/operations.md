Operations
==========

The following operations are available. Please note that some of the operations can be chained, e.g.

```python
data = {
    'paths': [...],
    'operations': [
        {
            'operation': 'create_mask',
            ...
        },
        {
            'operation': 'mask_mask',
            ...
        }
    ]
}
```

Please also note the examples given in the [examples](../examples) directory.

### Select bounding box

A rectangular bounding box can be selected using:

```python
response = requests.post('https://files.isimip.org/api/v2', json={
    'paths': [...],
    'operations': [
        {
            'operation': 'select_bbox',
            'bbox': [
                -180                # west
                180,                # east
                -23.43651,          # south
                23.43651,           # north
            ],
            'compute_mean': False,  # optional: set to True to get a time series of the field mean
            'output_csv': False     # optional: set to True to get a CSV file instead of NetCDF
        }
    ]
})
```

The operation is performed using [CDO](https://code.mpimet.mpg.de/projects/cdo) using:

```bash
cdo -f nc4c -z zip_5 -L -sellonlatbox,WEST,EAST,SOUTH,NORTH IFILE OFILE
```

### Select point

A time series of a point can be selected using:

```python
response = requests.post('https://files.isimip.org/api/v2', json={
    'paths': [...],
    'operations': [
        {
            'operation': 'select_point',
            'point': [
                13.064332,  # longitude
                52.38051    # latitude
            ],
            'output_csv': False  # optional: set to True to get a CSV file instead of NetCDF
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
            'bbox': [
                -180                # west
                180,                # east
                -23.43651,          # south
                23.43651,           # north
            ],
            'compute_mean': False,  # optional: set to True to get a time series of the field mean
            'output_csv': False     # optional: set to True to get a CSV file instead of NetCDF
        }
    ]
})
```

The operation is performed using [CDO](https://code.mpimet.mpg.de/projects/cdo) using:

```bash
cdo -f nc4c -z zip_5 -L -masklonlatbox,WEST,EAST,SOUTH,NORTH IFILE OFILE
```

### Mask country

A country can be masked (i.e. everything outside is set to `missing_value`) using:

```python
response = requests.post('https://files.isimip.org/api/v2', json={
    'paths': [...],
    'operations': [
        {
            'operation': 'mask_country',
            'country': 'aus',       # three letter code for, e.g. australia
            'compute_mean': False,  # optional: set to True to get a time series of the field mean
            'output_csv': False     # optional: set to True to get a csv file instead of NetCDF
        }
    ]
})
```

The operation is performed using [CDO](https://code.mpimet.mpg.de/projects/cdo) using:

```bash
cdo -f nc4c -z zip_5 -L -ifthen -selname,m_AUS COUNTRYMASK IFILE OFILE
```

### Mask land only

The landmass (without antarctica) can be masked (i.e. the ocean is set to `missing_value`) using:

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

The operation is performed using a custom python script (using `geopandas`, `xarray`, `rioxarray`, and `shapely`).

### Cutout bounding box

Instead of using [CDO](https://code.mpimet.mpg.de/projects/cdo) to select a bounding box, the cut-out can also be performed using [ncks](https://nco.sourceforge.net/nco.html). This operation has a much better performance when applied to the high resolution data from [CHELSA-W5E5 v1.0: W5E5 v1.0 downscaled with CHELSA v2.0](https://doi.org/10.48364/ISIMIP.836809.3).

```python
response = requests.post('https://files.isimip.org/api/v2', json={
    'paths': [...],
    'operations': [
        {
            'operation': 'cutout_bbox',
            'bbox': [
                12.50,  # west
                13.50   # east
                47.25,  # south
                47.75,  # north
            ]
        }
    ]
})
```

The operation is performed using [ncks](https://nco.sourceforge.net/nco.html) using:

```bash
ncks -h -d lat,SOUTH,NORTH -d WEST,EAST IFILE OFILE
```

### Cutout point

As for the bounding box, we also provide an operation to create a time series for a point using [ncks](https://nco.sourceforge.net/nco.html). Again, this has a much better performance when applied to the high resolution data from [CHELSA-W5E5 v1.0: W5E5 v1.0 downscaled with CHELSA v2.0](https://doi.org/10.48364/ISIMIP.836809.3).

```python
response = requests.post('https://files.isimip.org/api/v2', json={
    'paths': [...],
    'operations': [
        {
            'operation': 'cutout_point',
            'point': [
                13.064332,  # longitude
                52.38051    # latitude
            ]
        }
    ]
})
```

The operation is performed using [ncks](https://nco.sourceforge.net/nco.html) using:

```bash
ncks -h -d lat,SOUTH,NORTH -d WEST,EAST IFILE OFILE
```

### Create mask

Mask can be created from vector based input file, namely [Shapefiles](https://en.wikipedia.org/wiki/Shapefile) or [GeoJSON files](https://en.wikipedia.org/wiki/GeoJSON). This operation is performed once and the resulting mask can then be used in the `mask_mask` operation. As for the `mask_mask` operation, the input file needs to be uploaded together with the JSON. This is done using the content type `multipart/form-data`. For a shapefile, the different files need to be in one zip file. If the input shapefile or GeoJSON contains multiple layers, a variable is created for each layer with the name `m_X`, where `X` is the index of the layer, e.g. `m_0`. The mask variable can then be used in the subsequent `mask_mask` operation.

Using `requests` the request can be performed like this:

```python
import json
from pathlib import Path

import requests

url = 'https://files.isimip.org/api/v2'

shape_path = 'path/to/shape.zip'

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
            'mask': 'shape.nc',
            'var': 'm_10'
        }
    ]
}

response = requests.post(url, files={
    'data': json.dumps(data),
    'shape.zip': Path(shape_path).read_bytes(),
})
```
