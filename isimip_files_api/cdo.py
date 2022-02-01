import csv
import subprocess
import logging

from .netcdf import get_index
from .settings import (CDO_BIN,
                       COUNTRYMASKS_FILE_PATH,
                       LANDSEAMASK_FILE_PATH)
from .utils import mask_cmd


def mask_bbox(dataset_path, output_path, bbox):
    # cdo -f nc4c -z zip_5 -masklonlatbox,WEST,EAST,SOUTH,NORTH IFILE OFILE
    south, north, west, east = bbox
    return cdo('-f', 'nc4c',
               '-z', 'zip_5',
               '-masklonlatbox,{:f},{:f},{:f},{:f}'.format(west, east, south, north),
               str(dataset_path),
               str(output_path))


def mask_country(dataset_path, output_path, country):
    # cdo -f nc4c -z zip_5 -ifthen -selname,m_COUNTRY COUNTRYMASK IFILE OFILE
    return cdo('-f', 'nc4c',
               '-z', 'zip_5',
               '-ifthen',
               '-selname,m_{:3.3}'.format(country.upper()),
               str(COUNTRYMASKS_FILE_PATH),
               str(dataset_path),
               str(output_path))


def mask_landonly(dataset_path, output_path):
    # cdo -f nc4c -z zip_5 -ifthen LANDSEAMASK IFILE OFILE
    return cdo('-f', 'nc4c',
               '-z', 'zip_5',
               '-ifthen',
               str(LANDSEAMASK_FILE_PATH),
               str(dataset_path),
               str(output_path))


def select_point(dataset_path, output_path, point):
    # cdo -s outputtab,date,value,nohead -selindexbox,IX,IX,IY,IY IFILE
    ix, iy = get_index(dataset_path, point)
    return cdo('-s',
               'outputtab,date,value,nohead',
               '-selindexbox,{:d},{:d},{:d},{:d}'.format(ix, ix, iy, iy),
               str(dataset_path),
               output_path=output_path)


def select_bbox(dataset_path, output_path, bbox):
    # cdo -s outputtab,date,value,nohead -fldmean -sellonlatbox,WEST,EAST,SOUTH,NORTH IFILE
    south, north, west, east = bbox
    return cdo('-s',
               'outputtab,date,value,nohead',
               '-fldmean',
               '-sellonlatbox,{:f},{:f},{:f},{:f}'.format(west, east, south, north),
               str(dataset_path),
               output_path=output_path)


def select_country(dataset_path, output_path, country):
    # cdo -s outputtab,date,value,nohead -fldmean -ifthen -selname,m_COUNTRY COUNTRYMASK IFILE
    return cdo('-s',
               'outputtab,date,value,nohead',
               '-fldmean',
               '-ifthen',
               '-selname,m_{:3.3}'.format(country.upper()),
               str(COUNTRYMASKS_FILE_PATH),
               str(dataset_path),
               output_path=output_path)


def cdo(*args, output_path=None):
    cmd_args = [CDO_BIN] + list(args)
    cmd = ' '.join(cmd_args)
    env = {
        'CDI_VERSION_INFO': '0',
        'CDO_VERSION_INFO': '0',
        'CDO_HISTORY_INFO': '0'
    }

    logging.debug(cmd)
    output = subprocess.check_output(cmd_args, env=env)

    if output_path:
        with open(output_path, 'w', newline='') as fp:
            writer = csv.writer(fp, delimiter=',')
            for line in output.splitlines():
                writer.writerow(line.decode().strip().split())

    return mask_cmd(cmd)
