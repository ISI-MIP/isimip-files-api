from flask import current_app as app

import geopandas
import netCDF4 as nc
import numpy as np
import rioxarray  # noqa: F401
import shapely
import xarray as xr

from isimip_files_api.netcdf import get_grid
from isimip_files_api.operations import BaseOperation, MaskOperationMixin

FILL_VALUE_FLOAT = 1e+20
FILL_VALUE_BOOL = -128


class CreateMaskOperation(MaskOperationMixin, BaseOperation):

    operation = 'create_mask'
    perform_once = True

    def execute(self, job_path, input_path, output_path):
        # get the shape and mask from the config
        shape_file = job_path / self.config.get('shape')
        mask_file = job_path / self.config.get('mask')

        # get the resolution of the mask from the (first) input file, in arcsec
        grid = get_grid(input_path)

        # create a cmd string for log and README
        cmd = f'CreateMaskOperation.create_mask({shape_file.name}, {mask_file.name}, {grid})'
        app.logger.debug(cmd)

        # create the mask file
        self.create_mask(shape_file, mask_file, grid)

        # add the input and the output path of the command to the commands artefacts
        self.artefacts = [shape_file, mask_file]

        # return the command without the paths
        return cmd

    def validate_shape(self):
        if 'shape' not in self.config:
            return [f'shape is missing for operation "{self.operation}"']

    def validate_uploads(self, uploads):
        if 'shape' in self.config:
            shape = self.config['shape']
            if not uploads.get(shape):
                return [f'File "{shape}" for operation "{self.operation}" is not part of the uploads']

    def create_mask(self, shape_file, mask_file, grid):
        # get number of gridpoints and spacing
        n_lon, n_lat = grid
        d_lon = 360.0 / n_lon
        d_lat = 180.0 / n_lat

        # read shapefile/geojson using geopandas
        df = geopandas.read_file(shape_file)

        # create a diskless netcdf file using python-netCDF4
        ds = nc.Dataset(mask_file, 'w', format='NETCDF4_CLASSIC', diskless=True)
        ds.createDimension('lon', n_lon)
        ds.createDimension('lat', n_lat)

        # create lon variable
        lon = ds.createVariable('lon', 'f8', ('lon',), fill_value=FILL_VALUE_FLOAT)
        lon.standard_name = 'longitude'
        lon.long_name = 'Longitude'
        lon.units = 'degrees_east'
        lon.axis = 'X'
        lon[:] = np.arange(-180 + 0.5 * d_lon, 180, d_lon)

        # create lat variable
        lat = ds.createVariable('lat', 'f8', ('lat',), fill_value=FILL_VALUE_FLOAT)
        lat.standard_name = 'latitude'
        lat.long_name = 'Latitude'
        lat.units = 'degrees_north'
        lat.axis = 'Y'
        lat[:] = np.arange(90 - 0.5 * d_lat, -90, -d_lat)

        # create mask variable, with the properties of the shape
        for index, row in df.iterrows():
            variable_name = f'm_{index}'
            variable = ds.createVariable(variable_name, 'b', ('lat', 'lon'),
                                         fill_value=FILL_VALUE_BOOL, compression='zlib')

            for key, value in row.items():
                if isinstance(value, (str, int, float)):
                    setattr(variable, key.lower(), value)

            variable[:, :] = np.ones((n_lat, n_lon))

        # convert to a crs-aware xarray dataset
        ds = xr.open_dataset(xr.backends.NetCDF4DataStore(ds))
        ds.rio.write_crs(df.crs, inplace=True)

        # loop over shape variables and create masks
        for index, row in df.iterrows():
            variable_name = f'm_{index}'
            variable = ds[variable_name]

            geometry = shapely.geometry.mapping(row['geometry'])

            mask = variable.rio.clip([geometry], drop=False)
            variable[:, :] = mask[:, :]

        # write mask netcdf files
        ds.to_netcdf(mask_file)
