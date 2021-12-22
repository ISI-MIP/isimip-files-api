import csv
import subprocess
import logging

from .netcdf import get_index
from .settings import (CDO_BIN,
                       COUNTRYMASKS_FILE_PATH,
                       LANDSEAMASK_FILE_PATH)


def mask_bbox(dataset_path, output_path, bbox):
    # cdo -masklonlatbox,WEST,EAST,SOUTH,NORTH IFILE OFILE
    south, north, west, east = bbox
    cdo('-masklonlatbox,{:f},{:f},{:f},{:f}'.format(west, east, south, north),
        str(dataset_path),
        str(output_path))


def mask_country(dataset_path, output_path, country):
    # cdo -div IFILE -setctomiss,0 -selname,m_COUNTRY COUNTRYMASK OFILE
    cdo('-div',
        str(dataset_path),
        '-setctomiss,0',
        '-selname,m_{:3.3}'.format(country.upper()),
        str(COUNTRYMASKS_FILE_PATH), str(output_path))


def mask_landonly(dataset_path, output_path):
    # cdo -div IFILE -setctomiss,0 -selname,mask LANDSEAMASK OFILE
    cdo('-div',
        str(dataset_path),
        '-setctomiss,0',
        '-selname,mask',
        str(LANDSEAMASK_FILE_PATH),
        str(output_path))


def select_point(dataset_path, output_path, point):
    # cdo -s outputtab,date,value,nohead -fldmean -selindexbox,IX,IX,IY,IY IFILE
    ix, iy = get_index(dataset_path, point)
    output = cdo('-s',
                 'outputtab,date,value,nohead',
                 '-fldmean',
                 '-selindexbox,{:d},{:d},{:d},{:d}'.format(ix, ix, iy, iy),
                 str(dataset_path))
    write_csv(output, output_path)


def select_bbox(dataset_path, output_path, bbox):
    # cdo -s outputtab,date,value,nohead -fldmean -sellonlatbox,WEST,EAST,SOUTH,NORTH IFILE
    south, north, west, east = bbox
    output = cdo('-s',
                 'outputtab,date,value,nohead',
                 '-fldmean',
                 '-sellonlatbox,{:f},{:f},{:f},{:f}'.format(west, east, south, north),
                 str(dataset_path))
    write_csv(output, output_path)


def select_country(dataset_path, output_path, country):
    # cdo -s outputtab,date,value,nohead -fldmean -div IFILE -setctomiss,0 -selname,m_COUNTRY COUNTRYMASK
    output = cdo('-s',
                 'outputtab,date,value,nohead',
                 '-fldmean',
                 '-div',
                 str(dataset_path),
                 '-setctomiss,0',
                 '-selname,m_{:3.3}'.format(country.upper()),
                 str(COUNTRYMASKS_FILE_PATH))
    write_csv(output, output_path)


def cdo(*args):
    cmd = [CDO_BIN] + list(args)
    cmd_string = ' '.join(cmd)
    env = {
        'CDI_VERSION_INFO': '0',
        'CDO_VERSION_INFO': '0',
        'CDO_HISTORY_INFO': '0'
    }

    logging.debug(cmd_string)
    return subprocess.check_output(cmd, env=env)


def write_csv(output, output_path):
    with open(output_path, 'w', newline='') as fp:
        writer = csv.writer(fp, delimiter=',')
        for line in output.splitlines():
            writer.writerow(line.decode().strip().split())
