import shutil
from pathlib import Path
from tempfile import mkdtemp
from zipfile import ZipFile

from rq import get_current_job

from .settings import (INPUT_PATH, OUTPUT_PATH, OUTPUT_PREFIX)
from .utils import get_output_name, get_zip_file_name
from .netcdf import mask_bbox, mask_country, mask_landonly


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

        if args['bbox']:
            mask_bbox(input_path, tmp_path, args['bbox'])
        elif args['country']:
            mask_country(input_path, tmp_path, args['country'])
        elif args['landonly']:
            mask_landonly(input_path, tmp_path)

        if tmp_path.is_file():
            z.write(tmp_path, tmp_name)
        else:
            error_path = Path(tmp_path).with_suffix('.txt')
            error_path.write_text('Error: Original file could not be masked. Probably it is not using a global grid.')
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
