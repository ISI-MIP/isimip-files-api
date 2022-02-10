import logging
import subprocess

from .settings import NCKS_BIN
from .utils import mask_cmd


def cutout_bbox(dataset_path, output_path, bbox):
    # ncks -O -h -d lat,SOUTH,NORTH -d lon,WEST,EAST IFILE OFILE
    south, north, west, east = bbox
    return ncks(
        '-O',                                        # overwrite
        '-h',                                        # omit history
        '-d', 'lat,{:f},{:f}'.format(south, north),  # longitude
        '-d', 'lon,{:f},{:f}'.format(west, east),    # latitude
        str(dataset_path),                           # input
        str(output_path)                             # output
    )


def ncks(*args):
    cmd_args = [NCKS_BIN] + list(args)
    cmd = ' '.join(cmd_args)

    logging.debug(cmd)
    subprocess.check_output(cmd_args)

    return mask_cmd(cmd)
