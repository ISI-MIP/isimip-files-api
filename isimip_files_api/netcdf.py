import numpy as np
import numpy.ma as ma

from netCDF4 import Dataset

from .settings import (COUNTRYMASKS_FILE_PATH,
                       LANDSEAMASK_FILE_PATH)
from .validators import validate_dataset


def mask_bbox(dataset_path, output_path, bbox):
    with Dataset(dataset_path) as ds_in:
        if validate_dataset(ds_in):
            lat = ds_in.variables['lat'][:]
            lon = ds_in.variables['lon'][:]

            south, north, west, east = bbox

            where_lat = np.where((lat > south) & (lat < north))[0]
            where_lon = np.where((lon > west) & (lon < east))[0]

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


def copy_data(ds_in, ds_out, mask):
    # create dimensions
    for dimension_name, dimension in ds_in.dimensions.items():
        ds_out.createDimension(dimension_name, len(dimension) if not dimension.isunlimited() else None)

    # create variables
    for variable_name, variable in ds_in.variables.items():
        # try to get the fill value from the input variable
        try:
            fill_value = variable._FillValue
        except AttributeError:
            fill_value = None

        var = ds_out.createVariable(variable_name, variable.datatype, variable.dimensions,
                                    zlib=True, fill_value=fill_value)
        var.setncatts({k: v for k, v in variable.__dict__.items() if not k.startswith('_')})

        if variable_name in ['lat', 'lon', 'time']:
            var[:] = variable[:]
        else:
            var_mask = np.broadcast_to(mask, var.shape)
            var[...] = ma.masked_array(variable[...], var_mask)

    # copy global attributes
    ds_in.setncatts(ds_out.__dict__)
