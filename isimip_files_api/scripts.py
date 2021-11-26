#!/usr/bin/env python
import os
import argparse
from pathlib import Path

from dotenv import load_dotenv
from redis import Redis
from rq.exceptions import NoSuchJobError
from rq.job import Job

from .settings import OUTPUT_PATH
from .nco import cutout_bbox
from .netcdf import mask_bbox, mask_country, mask_landonly, select_bbox, select_country, select_point
from .utils import get_output_name

redis = Redis()


class FloatListAction(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, [float(c) for c in values.split(',')])


def parse_floats(string):
    return [float(c) for c in string.bbox.split(',')] if string else None


def select():
    parser = argparse.ArgumentParser()
    parser.add_argument('paths', nargs='+', help='List of files to mask')
    parser.add_argument('--point', help='Select by point, e.g. "52.39, 13.06"', action=FloatListAction)
    parser.add_argument('--country', help='Select by country, e.g. "deu"')
    parser.add_argument('--bbox', help='Select by bounding box, e.g. "-23.43651,23.43651,-180,180"', action=FloatListAction)
    parser.add_argument('--output', help='Output directory, default: .', default='.')
    args = parser.parse_args()

    if not any([args.country, args.bbox, args.point]):
        parser.error('Please provide at least --country, --bbox, or --point.')

    for path in args.paths:
        input_path = Path(path)
        output_path = Path(args.output).expanduser() / get_output_name(path, vars(args), suffix='.csv')

        if args.bbox:
            select_bbox(input_path, output_path, args.bbox)
        elif args.country:
            select_country(input_path, output_path, args.country)
        elif args.point:
            select_point(input_path, output_path, args.point)


def mask():
    parser = argparse.ArgumentParser()
    parser.add_argument('paths', nargs='+', help='List of files to mask')
    parser.add_argument('--country', help='Mask by country, e.g. "deu"')
    parser.add_argument('--bbox', help='Mask by bounding box, e.g. "-23.43651,23.43651,-180,180"')
    parser.add_argument('--landonly', action='store_true', help='Mask only land data')
    parser.add_argument('--output', help='Output directory, default: .', default='.')
    parser_args = parser.parse_args()

    if not any([parser_args.country, parser_args.bbox, parser_args.landonly]):
        parser.error('Please provide at least --country, --bbox, or --landonly.')

    args = {
        'country': parser_args.country,
        'bbox': [float(c) for c in parser_args.bbox.split(',')],
        'landonly': parser_args.landonly
    }

    for path in parser_args.paths:
        input_path = Path(path)
        output_path = Path(parser_args.output).expanduser() / get_output_name(path, args)

        if args['bbox']:
            mask_bbox(input_path, output_path, args['bbox'])
        elif args['country']:
            mask_country(input_path, output_path, args['country'])
        elif args['landonly']:
            mask_landonly(input_path, output_path)


def cutout():
    parser = argparse.ArgumentParser()
    parser.add_argument('paths', nargs='+', help='List of files to mask')
    parser.add_argument('--bbox', help='Mask by bounding box (south, north, west, east), e.g. "-23.43,23.43,-180,180"')
    parser.add_argument('--output', help='Output directory, default: .', default='.')
    parser_args = parser.parse_args()

    if not any([parser_args.bbox]):
        parser.error('Please provide at least --bbox.')

    args = {
        'bbox': [float(c) for c in parser_args.bbox.split(',')]
    }

    for path in parser_args.paths:
        input_path = Path(path)
        output_path = Path(parser_args.output).expanduser() / get_output_name(path, args)

        cutout_bbox(input_path, output_path, args['bbox'])


def clean():
    load_dotenv(Path().cwd() / '.env')

    for root, dirs, files in os.walk(OUTPUT_PATH, topdown=False):
        root_path = Path(root)

        for file_name in files:
            file_path = root_path / file_name

            # construct relative path and job_id
            path = root_path.relative_to(OUTPUT_PATH) / file_name
            job_id = path.stem.split('-')[-1]

            # check if there is a job for this
            try:
                Job.fetch(job_id, connection=redis)
            except NoSuchJobError:
                os.remove(file_path)

        # remove empty directories
        for dir_name in dirs:
            dir_path = root_path / dir_name
            if not os.listdir(dir_path):
                os.rmdir(dir_path)
