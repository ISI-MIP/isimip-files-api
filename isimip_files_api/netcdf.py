from flask import current_app as app

from netCDF4 import Dataset


def open_dataset(path):
    return Dataset(path)


def check_resolution(ds, resolution):
    try:
        lat_size, lon_size = app.config['RESOLUTIONS'][resolution]
        return ds.dimensions['lat'].size == lat_size or ds.dimensions['lon'].size == lon_size
    except KeyError:
        return False


def get_index(path, point):
    with Dataset(path) as ds:
        lat, lon = point

        dx = ds.variables['lon'][1] - ds.variables['lon'][0]
        dy = ds.variables['lat'][1] - ds.variables['lat'][0]

        ix = round(float((lon - ds.variables['lon'][0]) / dx))
        iy = round(float((lat - ds.variables['lat'][0]) / dy))

        return ix, iy


def get_grid(path):
    with Dataset(path) as ds:
        return (ds.variables['lon'][:], ds.variables['lat'][:])


def get_resolution(path):
    with Dataset(path) as ds:
        return (ds.dimensions['lon'].size, ds.dimensions['lat'].size)
