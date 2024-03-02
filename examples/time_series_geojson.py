import json
import time
from pathlib import Path

import requests

url = 'http://localhost:5000/'

paths = [
    'ISIMIP3b/InputData/climate/atmosphere/bias-adjusted/global/daily/ssp585/GFDL-ESM4/gfdl-esm4_r1i1p1f1_w5e5_ssp585_tas_global_daily_2015_2020.nc',
    'ISIMIP3b/InputData/climate/atmosphere/bias-adjusted/global/daily/ssp585/GFDL-ESM4/gfdl-esm4_r1i1p1f1_w5e5_ssp585_tas_global_daily_2021_2030.nc',
    'ISIMIP3b/InputData/climate/atmosphere/bias-adjusted/global/daily/ssp585/GFDL-ESM4/gfdl-esm4_r1i1p1f1_w5e5_ssp585_tas_global_daily_2031_2040.nc',
    'ISIMIP3b/InputData/climate/atmosphere/bias-adjusted/global/daily/ssp585/GFDL-ESM4/gfdl-esm4_r1i1p1f1_w5e5_ssp585_tas_global_daily_2041_2050.nc',
    'ISIMIP3b/InputData/climate/atmosphere/bias-adjusted/global/daily/ssp585/GFDL-ESM4/gfdl-esm4_r1i1p1f1_w5e5_ssp585_tas_global_daily_2051_2060.nc',
    'ISIMIP3b/InputData/climate/atmosphere/bias-adjusted/global/daily/ssp585/GFDL-ESM4/gfdl-esm4_r1i1p1f1_w5e5_ssp585_tas_global_daily_2061_2070.nc',
    'ISIMIP3b/InputData/climate/atmosphere/bias-adjusted/global/daily/ssp585/GFDL-ESM4/gfdl-esm4_r1i1p1f1_w5e5_ssp585_tas_global_daily_2071_2080.nc',
    'ISIMIP3b/InputData/climate/atmosphere/bias-adjusted/global/daily/ssp585/GFDL-ESM4/gfdl-esm4_r1i1p1f1_w5e5_ssp585_tas_global_daily_2081_2090.nc',
    'ISIMIP3b/InputData/climate/atmosphere/bias-adjusted/global/daily/ssp585/GFDL-ESM4/gfdl-esm4_r1i1p1f1_w5e5_ssp585_tas_global_daily_2091_2100.nc',
]

shape_path = Path('testing') / 'shapes' / 'pm.json'

data = {
    'paths': paths,
    'operations': [
        {
            'operation': 'create_mask',
            'shape': 'pm.json',
            'mask': 'pm.nc'
        },
        {
            'operation': 'mask_mask',
            'mask': 'pm.nc',
        },
        {
            'operation': 'compute_mean',
        },
        {
            'operation': 'output_csv'
        }
    ]
}

response = requests.post(url, files={
    'data': json.dumps(data),
    'pm.json': shape_path.read_bytes(),
})

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
    with requests.get(job['file_url'], stream=True) as response:
        with open(job['file_name'], 'wb') as fp:
            for chunk in response.iter_content(chunk_size=8192):
                 fp.write(chunk)
