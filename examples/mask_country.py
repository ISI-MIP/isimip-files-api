import time
import zipfile
from pathlib import Path

# install required dependencies with `pip install requests structlog`
import requests
import structlog

log = structlog.get_logger()

url = 'https://files.isimip.org/api/v2'

paths = [
    'ISIMIP3b/InputData/climate/atmosphere/bias-adjusted/global/daily/ssp585/GFDL-ESM4/gfdl-esm4_r1i1p1f1_w5e5_ssp585_tas_global_daily_2015_2020.nc'
]

data = {
    'paths': paths,
    'operations': [
        {
            'operation': 'mask_country',
            'country': 'aus',       # three letter code for, e.g. australia
            'compute_mean': False,  # optional: set to True to get a time series of the field mean
            'output_csv': False     # optional: set to True to get a CSV file instead of NetCDF
        }
    ]
}

download_path = 'download'

# perform the initial request to the server
response = requests.post(url, json=data)

# extract the job object from the response
try:
    job = response.json()
    log.info('job submitted', id=job['id'], status=job['status'])
except requests.exceptions.JSONDecodeError:
    log.info('job submission failed', error=response.text)
else:
    while job['status'] in ['queued', 'started']:
        # wait for 4 sec
        time.sleep(4)

        # check the status of the job
        job = requests.get(job['job_url']).json()
        log.info('job updated', id=job['id'], status=job['status'], meta=job['meta'])

    if job['status'] == 'finished':
        # download file
        zip_path = Path(download_path) / job['file_name']
        zip_path.parent.mkdir(exist_ok=True)
        log.info('downloading', file_url=job['file_url'])
        with requests.get(job['file_url'], stream=True) as response:
            with zip_path.open('wb') as fp:
                for chunk in response.iter_content(chunk_size=8192):
                     fp.write(chunk)

        # extract zip file
        out_path = zip_path.with_suffix('')
        out_path.mkdir(exist_ok=True)
        log.info('extracting', zip_path=str(out_path.resolve()))
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(out_path)
