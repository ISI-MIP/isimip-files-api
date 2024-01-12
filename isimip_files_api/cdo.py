import csv
import logging
import subprocess
from pathlib import Path

from flask import current_app as app

from .netcdf import get_index
from .utils import mask_cmd


def mask_bbox(dataset_path, output_path, bbox):
    # cdo -f nc4c -z zip_5 -masklonlatbox,WEST,EAST,SOUTH,NORTH IFILE OFILE
    south, north, west, east = bbox
    return cdo('-f', 'nc4c',
               '-z', 'zip_5',
               f'-masklonlatbox,{west:f},{east:f},{south:f},{north:f}',
               str(dataset_path),
               str(output_path))


def mask_country(dataset_path, output_path, country):
    # cdo -f nc4c -z zip_5 -ifthen -selname,m_COUNTRY COUNTRYMASK IFILE OFILE
    mask_path = Path(app.config['COUNTRYMASKS_FILE_PATH']).expanduser()
    return cdo('-f', 'nc4c',
               '-z', 'zip_5',
               '-ifthen',
               f'-selname,m_{country.upper():3.3}',
               str(mask_path),
               str(dataset_path),
               str(output_path))


def mask_landonly(dataset_path, output_path):
    # cdo -f nc4c -z zip_5 -ifthen LANDSEAMASK IFILE OFILE
    mask_path = Path(app.config['LANDSEAMASK_FILE_PATH']).expanduser()
    return cdo('-f', 'nc4c',
               '-z', 'zip_5',
               '-ifthen',
               str(mask_path),
               str(dataset_path),
               str(output_path))


def select_point(dataset_path, output_path, point):
    # cdo -s outputtab,date,value,nohead -selindexbox,IX,IX,IY,IY IFILE
    ix, iy = get_index(dataset_path, point)

    # add one since cdo is counting from 1!
    ix, iy = ix + 1, iy + 1

    return cdo('-s',
               'outputtab,date,value,nohead',
               f'-selindexbox,{ix:d},{ix:d},{iy:d},{iy:d}',
               str(dataset_path),
               output_path=output_path)


def select_bbox(dataset_path, output_path, bbox):
    # cdo -s outputtab,date,value,nohead -fldmean -sellonlatbox,WEST,EAST,SOUTH,NORTH IFILE
    south, north, west, east = bbox
    return cdo('-s',
               'outputtab,date,value,nohead',
               '-fldmean',
               f'-sellonlatbox,{west:f},{east:f},{south:f},{north:f}',
               str(dataset_path),
               output_path=output_path)


def select_country(dataset_path, output_path, country):
    # cdo -s outputtab,date,value,nohead -fldmean -ifthen -selname,m_COUNTRY COUNTRYMASK IFILE
    mask_path = Path(app.config['COUNTRYMASKS_FILE_PATH']).expanduser()
    return cdo('-s',
               'outputtab,date,value,nohead',
               '-fldmean',
               '-ifthen',
               f'-selname,m_{country.upper():3.3}',
               str(mask_path),
               str(dataset_path),
               output_path=output_path)


def cdo(*args, output_path=None):
    cmd_args = [app.config['CDO_BIN'], *list(args)]
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
