import subprocess

from .settings import NCKS_BIN


def cutout_bbox(dataset_path, output_path, bbox):
    south, north, west, east = bbox
    cmd = [
        NCKS_BIN,
        '-O',                                        # overwrite
        '-h',                                        # omit history
        '-d', 'lat,{:f},{:f}'.format(south, north),  # longitude
        '-d', 'lon,{:f},{:f}'.format(west, east),    # latitude
        str(dataset_path),                           # input
        str(output_path)                             # output
    ]
    subprocess.check_call(cmd)
