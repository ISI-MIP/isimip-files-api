import json
import time
import zipfile
from pathlib import Path

import requests

url = 'https://files.isimip.org/api/v2'

paths = [
    'ISIMIP3a/InputData/climate/atmosphere/obsclim/global/daily/historical/CHELSA-W5E5v1.0/chelsa-w5e5v1.0_obsclim_tas_30arcsec_global_daily_197901.nc'
]

data = {
    'paths': paths,
    'operations': [
        {
            'operation': 'cutout_bbox',
            'bbox': [
                47.25,  # south
                47.75,  # north
                12.50,  # east
                13.50   # west
            ]
        }
    ]
}

download_path = 'download'

# perform the initial request to the server
response = requests.post(url, json=data)

# extract the job object from the response
job = response.json()
print(json.dumps(job, indent=2))

for i in range(100):
    # check the status of the job
    job = requests.get(job['job_url']).json()
    print(json.dumps(job, indent=2))

    if job['status'] in ['queued', 'started']:
        time.sleep(4)  # wait for 4 sec
    else:
        break

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
