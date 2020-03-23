import numpy as np
from netCDF4 import Dataset

from .settings import COUNTRYMASKS_FILE_PATH, INPUT_PATH, OUTPUT_PATH
from .utils import perform_cutout
from .validators import validate_dataset


def cutout_bbox(dataset_path, cutout_path, bbox):
    cutout_path.parent.mkdir(parents=True, exist_ok=True)

    with Dataset(INPUT_PATH / dataset_path, 'r', format='NETCDF4') as ds:
        if validate_dataset(ds):
            lat = ds.variables['lat'][:]
            lon = ds.variables['lon'][:]

            lat_min, lat_max, lon_min, lon_max = bbox

            where_lat = np.where((lat > lat_min) & (lat < lat_max))[0]
            where_lon = np.where((lon > lon_min) & (lon < lon_max))[0]

            ilat0, ilat1 = where_lat[0], where_lat[-1] + 1
            ilon0, ilon1 = where_lon[0], where_lon[-1] + 1

            with Dataset(OUTPUT_PATH / cutout_path, 'w', format='NETCDF4') as co:
                perform_cutout(ds, co, ilat0, ilat1, ilon0, ilon1)


def cutout_country(dataset_path, cutout_path, country):
    cutout_path.parent.mkdir(parents=True, exist_ok=True)

    with Dataset(INPUT_PATH / dataset_path, 'r', format='NETCDF4') as ds:
        if validate_dataset(ds):
            with Dataset(COUNTRYMASKS_FILE_PATH, 'r', format='NETCDF4') as cm:
                country_var = 'm_{}'.format(country.upper())
                where = np.where(cm[country_var][:, :] == 1)

                ilat0, ilat1 = np.min(where[0]), np.max(where[0]) + 1
                ilon0, ilon1 = np.min(where[1]), np.max(where[1]) + 1

                country_mask = cm[country_var][ilat0:ilat1, ilon0:ilon1]

                with Dataset(OUTPUT_PATH / cutout_path, 'w', format='NETCDF4') as co:
                    perform_cutout(ds, co, ilat0, ilat1, ilon0, ilon1, mask=country_mask)
