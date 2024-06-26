ISIMIP Files API
================

A webservice to asynchronously perform operations on NetCDF files before downloading them, using [Flask](https://palletsprojects.com/p/flask/) and [RQ](https://python-rq.org).

The service is deployed on https://files.isimip.org/api/v2 as part of the [ISIMIP Repository](https://data.isimip.org). The previous version of the API is available at https://files.isimip.org/api/v1.

Parts of the software were supported by [NFDI4Earth](https://www.nfdi4earth.de/) and were funded by the German Research Foundation (NFDI4Earth, DFG project no. 460036893, https://www.nfdi4earth.de/). More information about this project can be found at <https://git.rwth-aachen.de/nfdi4earth/pilotsincubatorlab/incubator/climate-impact-data-extraction>.


How does it work?
-----------------

![ISIMIP Files API overview](docs/overview.svg)

Clients communicate with the API using HTTP requests and JSON data:

1. The initial request contains the `paths` of the datasets and the `operations` to perform.
2. The server answers with a `job_id` and a `job_url`, which can be used1 to retrieve the status of the job.
3. The job is queued on the server using [RQ](https://python-rq.org) and [redis](https://redis.io),
   and is eventually picked up by a worker.
4. The worker is using [CDO](https://code.mpimet.mpg.de/projects/cdo/) or
   [NCKS](https://linux.die.net/man/1/ncks) or a custom script to perform each operation.
5. When the task is done, the output files are stored in a ZIP file on a static web server.
6. From there, the user can download the file, extract it and use it for their work 🚀.

The API can be used "raw", integrated into interactive web pages, or using scripts or notebooks.


Setup
-----

The API makes no assumptions about the files other than that they are globally gridded NetCDF files. In particular, no ISIMIP internal conventions are used. It can therefore be reused by other archives. Setup and deployment are described in [docs/install.md](docs/setup.md).


Usage
-----

The service is integrated into the [ISIMIP Repository](https://data.isimip.org) and is available from the search interface and the dataset and file pages through the "Configure downloads" link. This functionality currently uses version 1.1.1 of the API.

Version 2 of the API can be used with standard HTTP libraries (e.g. [requests](https://requests.readthedocs.io) for Python). While the following examples use the ISIMIP Repository, Python and `requests`, they should be transferable to other servers, languages or libraries.

A job is initiated by sending HTTP POST request to the root endpoint of the API. The request needs to use the content type `application/json` and contain a single JSON object with a list of `paths` and a list of `operations`. While the `paths` can be obtained from the [ISIMIP Repository](https://data.isimip.org) (e.g. `ISIMIP3b/InputData/climate/atmosphere/bias-adjusted/global/daily/ssp585/GFDL-ESM4/gfdl-esm4_r1i1p1f1_w5e5_ssp585_tas_global_daily_2015_2020.nc`), the operations are described in [docs/operations.md](docs/operations.md).

Using Python and `requests`, requests can be performed like this (e.g. for the selection of the time series for a point given by its longitude and latitude):

```python
import requests

response = requests.post('https://files.isimip.org/api/v2', json={
    'paths': [
        'ISIMIP3b/InputData/.../gfdl-esm4_r1i1p1f1_w5e5_ssp585_tas_global_daily_2015_2020.nc',
        'ISIMIP3b/InputData/.../gfdl-esm4_r1i1p1f1_w5e5_ssp585_tas_global_daily_2021_2030.nc',
        'ISIMIP3b/InputData/.../gfdl-esm4_r1i1p1f1_w5e5_ssp585_tas_global_daily_2031_2031.nc',
        ...
    ],
    'operations': [
        {
            'operation': 'select_point',
            'point': [52.380551, 13.064332]
        }
    ]
})

result = response.json()
```

The `result` is a dictionary describing the job on the server:

```json
{
    "id": "5741ca0e7f824d37ef23e107f5e5261a31e974a6",
    "job_url": "https://files.isimip.org/api/v2/5741ca0e7f824d37ef23e107f5e5261a31e974a6",
    "meta": {},
    "status": "queued",
    "ttl": 604800
}
```

Performing the initial request again, or performing a `GET` on the url given in `job_url`, will give an update on the job status, e.g.

```json
{
  "id": "5741ca0e7f824d37ef23e107f5e5261a31e974a6",
  "job_url": "https://files.isimip.org/api/v2/5741ca0e7f824d37ef23e107f5e5261a31e974a6",
  "meta": {
    "created_files": 0,
    "total_files": 1
  },
  "status": "started",
  "ttl": 604800
}
```

When the job is completed on the server the status becomes `finished` and the result contains a `file_name` and a `file_url`.

```json
{
  "file_name": "download-5741ca0e7f824d37ef23e107f5e5261a31e974a6.zip",
  "file_url": "https://files.isimip.org/api/v2/output/download-5741ca0e7f824d37ef23e107f5e5261a31e974a6.zip",
  "id": "5741ca0e7f824d37ef23e107f5e5261a31e974a6",
  "job_url": "https://files.isimip.org/api/v2/5741ca0e7f824d37ef23e107f5e5261a31e974a6",
  "meta": {
    "created_files": 1,
    "total_files": 1
  },
  "status": "finished",
  "ttl": 604800
}
```

The file can be downloaded under the URL given by `file_url` (if the output directory of the API is made public via a web server).

Please also note the examples given in the [examples](examples) directory.
