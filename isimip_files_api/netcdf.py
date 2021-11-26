from netCDF4 import Dataset


def open_dataset(path):
    return Dataset(path)


def check_halfdeg(ds):
    return ds.dimensions['lat'].size == 360 or ds.dimensions['lon'].size == 720


def check_30arcsec(ds):
    return ds.dimensions['lat'].size == 20880 or ds.dimensions['lon'].size == 43200


def get_index(path, point):
    with Dataset(path) as ds:
        lat, lon = point

        dx = ds.variables['lon'][1] - ds.variables['lon'][0]
        dy = ds.variables['lat'][1] - ds.variables['lat'][0]

        ix = int((lon - ds.variables['lon'][0]) / dx)

        if dy > 0:
            iy = int((lat - ds.variables['lat'][0]) / dy)
        else:
            iy = int((ds.variables['lat'][0] - lat) / -dy)

        return ix, iy
