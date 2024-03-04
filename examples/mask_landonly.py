import json
import time
import zipfile
from pathlib import Path

import requests

url = 'http://localhost:5000'

paths = [
    'ISIMIP3b/InputData/climate/atmosphere/bias-adjusted/global/daily/ssp585/GFDL-ESM4/gfdl-esm4_r1i1p1f1_w5e5_ssp585_tas_global_daily_2015_2020.nc'
]

data = {
    'paths': paths,
    'operations': [
        {
            'operation': 'mask_landonly'
        }
    ]
}

response = requests.post(url, json=data)

job = response.json()
print(json.dumps(job, indent=2))

for i in range(100):
    job = requests.get(job['job_url']).json()
    print(json.dumps(job, indent=2))

    if job['status'] in ['queued', 'started']:
        time.sleep(2)
    else:
        break

if job['status'] == 'finished':
    # download file
    zip_path = Path(job['file_name'])
    with requests.get(job['file_url'], stream=True) as response:
        with zip_path.open('wb') as fp:
            for chunk in response.iter_content(chunk_size=8192):
                 fp.write(chunk)

    # extract zip file
    out_path = Path(job['file_name']).with_suffix('')
    out_path.mkdir(exist_ok=True)
    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(out_path)
