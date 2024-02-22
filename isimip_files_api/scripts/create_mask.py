import argparse

import geopandas
import netCDF4 as nc
import numpy as np
import rioxarray  # noqa: F401
import shapely
import xarray as xr

FILL_VALUE_FLOAT = 1e+20
FILL_VALUE_BOOL = -128

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_path', help='path to the input file')
    parser.add_argument('output_path', help='path to the output file')
    parser.add_argument('-g|--grid', dest='grid', help='grid spacing in arcsec',
                        type=int, default=1800)

    args = parser.parse_args()

    n_lat = int((360 * 60 * 60) / args.grid)
    n_lon = int((180 * 60 * 60) / args.grid)
    delta = args.grid / 3600.0

    df = geopandas.read_file(args.input_path)

    # create a diskless netcdf file using python-netCDF4
    ds = nc.Dataset(args.output_path, 'w', format='NETCDF4_CLASSIC', diskless=True)
    ds.createDimension('lon', n_lat)
    ds.createDimension('lat', n_lon)

    lon = ds.createVariable('lon', 'f8', ('lon',), fill_value=FILL_VALUE_FLOAT)
    lon.standard_name = 'longitude'
    lon.long_name = 'Longitude'
    lon.units = 'degrees_east'
    lon.axis = 'X'
    lon[:] = np.arange(-180 + 0.5 * delta, 180, delta)

    lat = ds.createVariable('lat', 'f8', ('lat',), fill_value=FILL_VALUE_FLOAT)
    lat.standard_name = 'latitude'
    lat.long_name = 'Latitude'
    lat.units = 'degrees_north'
    lat.axis = 'Y'
    lat[:] = np.arange(90 - 0.5 * delta, -90 - 0.5 * delta, -delta)

    for index, row in df.iterrows():
        variable_name = f'm_{index}'
        variable = ds.createVariable(variable_name, 'b', ('lat', 'lon'),
                                     fill_value=FILL_VALUE_BOOL, compression='zlib')

        for key, value in row.items():
            if isinstance(value, (str, int, float)):
                setattr(variable, key.lower(), value)

        variable[:, :] = np.ones((n_lon, n_lat))

    # convert to a crs-aware xarray dataset
    ds = xr.open_dataset(xr.backends.NetCDF4DataStore(ds))
    ds.rio.write_crs(df.crs, inplace=True)

    for index, row in df.iterrows():
        variable_name = f'm_{index}'
        variable = ds[variable_name]

        geometry = shapely.geometry.mapping(row['geometry'])

        mask = variable.rio.clip([geometry], drop=False)
        variable[:, :] = mask[:, :]

    ds.to_netcdf(args.output_path)


if __name__ == '__main__':
    main()
