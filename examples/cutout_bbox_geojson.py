import json
import time
import zipfile
from pathlib import Path

# install required dependencies with `pip install requests structlog`
import requests
import structlog

log = structlog.get_logger()

url = 'https://files.isimip.org/api/v2'

paths = [
    'ISIMIP3a/InputData/climate/atmosphere/obsclim/global/daily/historical/CHELSA-W5E5/chelsa-w5e5_obsclim_tas_30arcsec_global_daily_197901.nc'
]

# a shapefile of e.g. switzerland can be downloaded at
# https://github.com/ISI-MIP/isipedia-countries/raw/master/country_data/CHE/country.geojson
shape_path = 'country.geojson'

data = {
    'paths': paths,
    'operations': [
        # first, cut-out a region around switzerland
        {
            'operation': 'cutout_bbox',
            'bbox': [
                 5.800,  # west
                10.600,  # east
                45.800,  # south
                47.900   # north
            ]
        },
        # next, create a mask from the shape with the resolution of the cut-out file
        {
            'operation': 'create_mask',
            'shape': 'che.geojson',
            'mask': 'che.nc',
        },
        # lastly, mask the file using the created mask
        {
            'operation': 'mask_mask',
            'mask': 'che.nc',
        }
    ]
}

download_path = 'download'

# perform the initial request to the server
response = requests.post(url, files={
    'data': json.dumps(data),
    'che.geojson': Path(shape_path).read_bytes(),  # needs to be the same as in the create_mask operation
})

try:
    response.raise_for_status()  # check if the request was successfull
    job = response.json()        # extract the job object from the response
except (requests.exceptions.HTTPError, requests.exceptions.JSONDecodeError):
    log.error('job submission failed', error=response.text)
else:
    log.info('job submitted', id=job.get('id'), status=job.get('status'))

    while job.get('status') in ['queued', 'started']:
        # wait for 4 sec
        time.sleep(4)

        # check the status of the job
        job = requests.get(job['job_url']).json()
        log.info('job updated', id=job['id'], status=job['status'], meta=job['meta'])

    if job.get('status') == 'finished':
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
