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
                       LANDSEAMASK_FILE_PATH, OUTPUT_PATH)
from .utils import find_files, get_output_name
from .validators import validate_dataset


def run_task(path, output_path, args):
    # find files
    files = find_files(path)

    # get current job and init metadata
    job = get_current_job()
    job.meta['output_path'] = str(output_path)
    job.meta['created_files'] = 0
    job.meta['total_files'] = len(files)
    job.save_meta()

    output_path = OUTPUT_PATH / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if Path(output_path).suffix == '.zip':
        # create a temporary directory
        tmp = Path(mkdtemp(prefix='isimip-files-api-'))

        # open zipfile
        z = ZipFile(output_path, 'w')

        for file_path in files:
            input_path = INPUT_PATH / file_path
            tmp_name = get_output_name(file_path, args)
            tmp_path = tmp / tmp_name

            if args['bbox']:
                mask_bbox(input_path, tmp_path, args['bbox'])
            elif args['country']:
                mask_country(input_path, tmp_path, args['country'])
            elif args['landonly']:
                mask_landonly(input_path, tmp_path)

            z.write(tmp_path, tmp_name)

            # update the current job and store progress
            job.meta['created_files'] += 1
            job.save_meta()

        # close zip file
        z.close()

        # delete temporary directory
        shutil.rmtree(tmp)

    else:
        input_path = INPUT_PATH / path

        if args['bbox']:
            mask_bbox(input_path, output_path, args['bbox'])
        elif args['country']:
            mask_country(input_path, output_path, args['country'])
        elif args['landonly']:
            mask_landonly(input_path, output_path)

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
