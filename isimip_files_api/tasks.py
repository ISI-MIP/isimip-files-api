import shutil
from pathlib import Path
from tempfile import mkdtemp
from zipfile import ZipFile

from flask import current_app as app

from rq import get_current_job

from .utils import get_zip_file_name


def run_task(paths, operations):
    # get current job and init metadata
    job = get_current_job()
    job.meta['created_files'] = 0
    job.meta['total_files'] = len(paths)
    job.save_meta()

    # create output paths
    output_path = Path(app.config['OUTPUT_PATH']).expanduser() / get_zip_file_name(job.id)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # create a temporary directory
    tmp = Path(mkdtemp(prefix=app.config['OUTPUT_PREFIX']))

    # open zipfile
    z = ZipFile(output_path, 'w')

    # open readme
    readme_path = tmp / 'README.txt'
    readme = readme_path.open('w')
    readme.write('The following commands were used to create the files in this container:\n\n')

    for path in paths:
        input_path = Path(app.config['INPUT_PATH']).expanduser() / path
        app.logger.warn(input_path)

        for operation in operations:
            print(operation)
            app.logger.error(operation)

        # if args['task'] in ['select_country', 'select_bbox', 'select_point']:
        #     tmp_name = get_output_name(path, args, suffix='.csv')
        # else:
        #     tmp_name = get_output_name(path, args)

        # tmp_path = tmp / tmp_name

        # if args['task'] == 'cutout_bbox':
        #     cmd = cutout_bbox(input_path, tmp_path, args['bbox'])

        # elif args['task'] == 'mask_country':
        #     cmd = mask_country(input_path, tmp_path, args['country'])

        # elif args['task'] == 'mask_bbox':
        #     cmd = mask_bbox(input_path, tmp_path, args['bbox'])

        # elif args['task'] == 'mask_landonly':
        #     cmd = mask_landonly(input_path, tmp_path)

        # elif args['task'] == 'select_country':
        #     cmd = select_country(input_path, tmp_path, args['country'])

        # elif args['task'] == 'select_bbox':
        #     cmd = select_bbox(input_path, tmp_path, args['bbox'])

        # elif args['task'] == 'select_point':
        #     cmd = select_point(input_path, tmp_path, args['point'])

        # # write cmd into readme file
        # readme.write(cmd + '\n')

        # if tmp_path.is_file():
        #     z.write(tmp_path, tmp_name)
        # else:
        #     error_path = Path(tmp_path).with_suffix('.txt')
        #     error_path.write_text('Something went wrong with processing the input file.'
        #                           ' Probably it is not using a global grid.')
        #     z.write(error_path, error_path.name)

        # # update the current job and store progress
        # job.meta['created_files'] += 1
        # job.save_meta()

    # close and write readme file
    readme.close()
    z.write(readme_path, readme_path.name)

    # close zip file
    z.close()

    # delete temporary directory
    shutil.rmtree(tmp)

    # return True to indicate success
    return True
