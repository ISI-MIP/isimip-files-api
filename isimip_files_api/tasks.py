import shutil
from pathlib import Path
from tempfile import mkdtemp
from zipfile import ZipFile

from rq import get_current_job

from .settings import (INPUT_PATH, OUTPUT_PATH, OUTPUT_PREFIX)
from .utils import get_output_name, get_zip_file_name
from .cdo import mask_bbox, mask_country, mask_landonly, select_country, select_bbox, select_point
from .nco import cutout_bbox


def run_task(paths, args):
    # get current job and init metadata
    job = get_current_job()
    job.meta['created_files'] = 0
    job.meta['total_files'] = len(paths)
    job.save_meta()

    # create output paths
    output_path = OUTPUT_PATH / get_zip_file_name(job.id)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # create a temporary directory
    tmp = Path(mkdtemp(prefix=OUTPUT_PREFIX))

    # open zipfile
    z = ZipFile(output_path, 'w')

    for path in paths:
        input_path = INPUT_PATH / path
        tmp_name = get_output_name(path, args)
        tmp_path = tmp / tmp_name

        if args['task'] == 'cutout_bbox':
            cutout_bbox(input_path, tmp_path, args['bbox'])

        elif args['task'] == 'mask_country':
            mask_country(input_path, tmp_path, args['country'])

        elif args['task'] == 'mask_bbox':
            mask_bbox(input_path, tmp_path, args['bbox'])

        elif args['task'] == 'mask_landonly':
            mask_landonly(input_path, tmp_path)

        elif args['task'] == 'select_point':
            select_point(input_path, tmp_path, args['point'])

        elif args['task'] == 'select_country':
            select_country(input_path, tmp_path, args['country'])

        elif args['task'] == 'select_bbox':
            select_bbox(input_path, tmp_path, args['bbox'])

        if tmp_path.is_file():
            z.write(tmp_path, tmp_name)
        else:
            error_path = Path(tmp_path).with_suffix('.txt')
            error_path.write_text('Something went wrong with processing the input file. Probably it is not using a global grid.')
            z.write(error_path, error_path.name)

        # update the current job and store progress
        job.meta['created_files'] += 1
        job.save_meta()

    # close zip file
    z.close()

    # delete temporary directory
    shutil.rmtree(tmp)

    # return True to indicate success
    return True
