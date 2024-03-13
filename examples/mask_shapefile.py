import json
import time
import zipfile
from pathlib import Path

import requests

url = 'https://files.isimip.org/api/v2'

paths = [
    'ISIMIP3b/InputData/climate/atmosphere/bias-adjusted/global/daily/ssp585/GFDL-ESM4/gfdl-esm4_r1i1p1f1_w5e5_ssp585_tas_global_daily_2015_2020.nc'
]

shape_path = 'testing/shapes/pm.zip'

data = {
    'paths': paths,
    'operations': [
        {
            'operation': 'create_mask',
            'shape': 'shape.zip',
            'mask': 'shape.nc',
        },
        {
            'operation': 'mask_mask',
            'mask': 'shape.nc',        # needs to be the same as in the create_mask operation
            'compute_mean': False,     # optional: set to True to get a time series of the field mean
            'output_csv': False,       # optional: set to True to get a CSV file instead of NetCDF
            'var': 'm_0'               # optional: use this mask variable, the number is the layer in the shapefile
        }
    ]
}

download_path = 'download'

# perform the initial request to the server
response = requests.post(url, files={
    'data': json.dumps(data),
    'shape.zip': Path(shape_path).read_bytes(),  # needs to be the same as in the create_mask operation
})

# extract the job object from the response
job = response.json()
print(json.dumps(job, indent=2))

while job['status'] in ['queued', 'started']:
    # wait for 4 sec
    time.sleep(4)

    # check the status of the job
    job = requests.get(job['job_url']).json()
    print(json.dumps(job, indent=2))

if job['status'] == 'finished':
    # download file
    zip_path = Path(download_path) / job['file_name']
    zip_path.parent.mkdir(exist_ok=True)
    with requests.get(job['file_url'], stream=True) as response:
        with zip_path.open('wb') as fp:
            for chunk in response.iter_content(chunk_size=8192):
                 fp.write(chunk)

    # extract zip file
    out_path = zip_path.with_suffix('')
    out_path.mkdir(exist_ok=True)
    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(out_path)
