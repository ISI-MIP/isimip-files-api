import json
import time
import zipfile
from pathlib import Path

import requests

url = 'https://files.isimip.org/api/v2'

paths = [
    'ISIMIP3b/InputData/climate/atmosphere/bias-adjusted/global/daily/ssp585/GFDL-ESM4/gfdl-esm4_r1i1p1f1_w5e5_ssp585_tas_global_daily_2015_2020.nc'
]

data = {
    'paths': paths,
    'operations': [
        {
            'operation': 'mask_bbox',
            'bbox': [
                -180,       # west
                 180,       # east
                -23.43651,  # south
                 23.43651,  # north
            ],
            'compute_mean': False,  # optional: set True to get a time series of the field mean
            'output_csv': False     # optional: set True to get a CSV file instead of NetCDF
        }
    ]
}

download_path = 'download'

# perform the initial request to the server
response = requests.post(url, json=data)

# extract the job object from the response
try:
    job = response.json()
    print(json.dumps(job, indent=2))
except requests.exceptions.JSONDecodeError:
    print(response.text)
else:
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
