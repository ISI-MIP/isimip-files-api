import hashlib
from pathlib import Path

import numpy as np
import numpy.ma as ma

from .settings import BASE_URL, OUTPUT_URL


def get_response(job, http_status):
    response = {
        'id': job.id,
        'job_url': BASE_URL + '/' + job.id,
        'meta': job.meta,
        'status': job.get_status(),
    }

    if job.get_status() == 'finished':
        if 'cutout_path' in job.meta:
            response['file_url'] = OUTPUT_URL + '/' + job.meta['cutout_path']

    return response, http_status


def get_errors_response(errors):
    return {
        'status': 'error',
        'errors': errors
    }, 400


def get_cutout_path(path, region):
    cutout_name = Path(path).name.replace(path.suffix, '_' + region + path.suffix)
    cutout_path = path.parent / cutout_name
    return str(cutout_path)


def get_hash(cutout_path):
    m = hashlib.sha1()
    m.update(str(cutout_path).encode())
    return m.hexdigest()


def perform_cutout(ds, co, ilat0, ilat1, ilon0, ilon1, mask=None):
    nlat = ilat1 - ilat0
    nlon = ilon1 - ilon0

    # create lat, lon, time dimensions
    co.createDimension("lat", nlat)
    co.createDimension("lon", nlon)
    co.createDimension('time', None)

    # create additional dimensions
    for key, dimension in ds.dimensions.items():
        if key not in ['lat', 'lon', 'time']:
            co.createDimension(key, len(dimension))

    # get new lat and lon arrays
    lat = ds.variables['lat'][ilat0:ilat1]
    lon = ds.variables['lon'][ilon0:ilon1]

    # create variables
    for key, variable in ds.variables.items():
        # get variable attributes and adjust for new lat/lon range
        atts = variable.__dict__.copy()
        if key == 'lat':
            atts['valid_min'] = np.min(lat)
            atts['valid_max'] = np.max(lat)
        elif key == 'lon':
            atts['valid_min'] = np.min(lon)
            atts['valid_max'] = np.max(lon)

        # create variable and attributes
        var = co.createVariable(key, variable.datatype, variable.dimensions)
        var.setncatts(atts)

    # copy global attributes
    co.setncatts(ds.__dict__)

    # copy data for lat, lon, time
    co.variables['lat'][:] = lat
    co.variables['lon'][:] = lon
    co.variables['time'][:] = ds.variables['time'][:]

    # copy data for the main variable(s)
    for key in ds.variables.keys():
        if key not in ['lat', 'lon', 'time']:
            var = ds.variables[key][..., ilat0:ilat1, ilon0:ilon1]

            if mask is not None:
                var_mask = np.broadcast_to(mask, var.shape)
                co.variables[key][..., :, :] = ma.masked_array(var[:], np.logical_not(var_mask))
            else:
                co.variables[key][..., :, :] = var
