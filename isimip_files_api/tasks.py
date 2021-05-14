import shutil
from pathlib import Path
from tempfile import mkdtemp
from zipfile import ZipFile

import numpy as np
import numpy.ma as ma
from netCDF4 import Dataset
from rq import get_current_job

from .netcdf import copy_data
from .settings import (COUNTRYMASKS_FILE_PATH, INPUT_PATH,
                       LANDSEAMASK_FILE_PATH, OUTPUT_PATH, OUTPUT_PREFIX)
from .utils import get_output_name, get_zip_file_name
from .validators import validate_dataset


def run_task(paths, args):
    # get current job and init metadata
    job = get_current_job()
    job.meta['created_files'] = 0
    job.meta['total_files'] = len(paths)
    job.save_meta()

    # create output paths
    output_path = OUTPUT_PATH / get_zip_file_name(job.id)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # create a temporary directory
    tmp = Path(mkdtemp(prefix=OUTPUT_PREFIX))

    # open zipfile
    z = ZipFile(output_path, 'w')

    for path in paths:
        input_path = INPUT_PATH / path
        tmp_name = get_output_name(path, args)
        tmp_path = tmp / tmp_name

        if args['bbox']:
            mask_bbox(input_path, tmp_path, args['bbox'])
        elif args['country']:
            mask_country(input_path, tmp_path, args['country'])
        elif args['landonly']:
            mask_landonly(input_path, tmp_path)

        if tmp_path.is_file():
            z.write(tmp_path, tmp_name)
        else:
            error_path = Path(tmp_path).with_suffix('.txt')
            error_path.write_text('Error: Original file could not be masked. Probably it is not using a global grid.')
            z.write(error_path, error_path.name)

        # update the current job and store progress
        job.meta['created_files'] += 1
        job.save_meta()

    # close zip file
    z.close()

    # delete temporary directory
    shutil.rmtree(tmp)

    # return True to indicate success
    return True


def mask_bbox(dataset_path, output_path, bbox):
    with Dataset(dataset_path) as ds_in:
        if validate_dataset(ds_in):
            lat = ds_in.variables['lat'][:]
            lon = ds_in.variables['lon'][:]

            lat_min, lat_max, lon_min, lon_max = bbox

            where_lat = np.where((lat > lat_min) & (lat < lat_max))[0]
            where_lon = np.where((lon > lon_min) & (lon < lon_max))[0]

            ilat0, ilat1 = where_lat[0], where_lat[-1] + 1
            ilon0, ilon1 = where_lon[0], where_lon[-1] + 1

            mask = np.ones((lat.shape[0], lon.shape[0]), dtype=bool)
            mask[ilat0:ilat1, ilon0:ilon1] = False

            with Dataset(output_path, 'w', format='NETCDF4_CLASSIC') as ds_out:
                copy_data(ds_in, ds_out, mask)


def mask_country(dataset_path, output_path, country):
    with Dataset(dataset_path) as ds_in:
        if validate_dataset(ds_in):
            with Dataset(COUNTRYMASKS_FILE_PATH) as cm:
                country_var = 'm_{}'.format(country.upper())
                country_mask = np.logical_not(cm[country_var][...])

                with Dataset(output_path, 'w', format='NETCDF4_CLASSIC') as ds_out:
                    copy_data(ds_in, ds_out, country_mask)


def mask_landonly(dataset_path, output_path):
    with Dataset(dataset_path) as ds_in:
        if validate_dataset(ds_in):
            with Dataset(LANDSEAMASK_FILE_PATH) as lsm:
                landsea_mask = np.logical_not(ma.filled(lsm['mask'][0, :, :], fill_value=0.0), dtype=bool)

                with Dataset(output_path, 'w', format='NETCDF4_CLASSIC') as ds_out:
                    copy_data(ds_in, ds_out, landsea_mask)
