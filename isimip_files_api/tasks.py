import numpy as np
import numpy.ma as ma
from netCDF4 import Dataset

from .netcdf import copy_data
from .settings import (COUNTRYMASKS_FILE_PATH, INPUT_PATH,
                       LANDSEAMASK_FILE_PATH, OUTPUT_PATH)
from .validators import validate_dataset


def mask_bbox(dataset_path, output_path, bbox):
    with Dataset(INPUT_PATH / dataset_path, 'r', format='NETCDF4') as ds:
        if validate_dataset(ds):
            lat = ds.variables['lat'][:]
            lon = ds.variables['lon'][:]

            lat_min, lat_max, lon_min, lon_max = bbox

            where_lat = np.where((lat > lat_min) & (lat < lat_max))[0]
            where_lon = np.where((lon > lon_min) & (lon < lon_max))[0]

            ilat0, ilat1 = where_lat[0], where_lat[-1] + 1
            ilon0, ilon1 = where_lon[0], where_lon[-1] + 1

            mask = np.ones((lat.shape[0], lon.shape[0]), dtype=bool)
            mask[ilat0:ilat1, ilon0:ilon1] = False

            output_path = OUTPUT_PATH / output_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with Dataset(output_path, 'w', format='NETCDF4') as co:
                copy_data(ds, co, mask)


def mask_country(dataset_path, output_path, country):
    with Dataset(INPUT_PATH / dataset_path, 'r', format='NETCDF4') as ds:
        if validate_dataset(ds):
            with Dataset(COUNTRYMASKS_FILE_PATH, 'r', format='NETCDF4') as cm:
                country_var = 'm_{}'.format(country.upper())
                country_mask = np.logical_not(cm[country_var][...])

                output_path = OUTPUT_PATH / output_path
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with Dataset(output_path, 'w', format='NETCDF4') as co:
                    copy_data(ds, co, country_mask)


def mask_landonly(dataset_path, output_path):
    with Dataset(INPUT_PATH / dataset_path, 'r', format='NETCDF4') as ds:
        if validate_dataset(ds):
            with Dataset(LANDSEAMASK_FILE_PATH, 'r', format='NETCDF4') as lsm:
                landsea_mask = np.logical_not(ma.filled(lsm['mask'][0, :, :], fill_value=0.0), dtype=bool)

                output_path = OUTPUT_PATH / output_path
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with Dataset(output_path, 'w', format='NETCDF4') as co:
                    copy_data(ds, co, landsea_mask)
