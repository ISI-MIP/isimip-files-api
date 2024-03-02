from pathlib import Path

from flask import current_app as app

from rq import get_current_job

from .operations import OperationRegistry
from .utils import get_input_path, get_job_path, get_zip_file, mask_paths, remove_job_path


def run_task(paths, operations):
    # get current job and init metadata
    job = get_current_job()
    job.meta['created_files'] = 0
    job.meta['total_files'] = len(paths)
    job.save_meta()

    # get the temporary directory
    job_path = get_job_path(job.id)

    # create the output zip file
    zip_file = get_zip_file(job.id)

    # open readme
    readme_path = job_path / 'README.txt'
    readme = readme_path.open('w')
    readme.write('The following commands were used to create the files in this container:\n\n')

    # construct command list from the operations
    command_list = OperationRegistry().get_command_list(operations)

    for path in paths:
        input_path = get_input_path() / path
        output_path = Path(input_path.name)
        output_region = None

        for command in command_list:
            if command.perform_once and path != paths[0]:
                continue

            # update region tag in output_path
            region = command.get_region()
            if region:
                if output_region is None:
                    if app.config['GLOBAL_TAG'] in output_path.name:
                        # replace the _global_ specifier
                        output_name = output_path.name.replace(app.config['GLOBAL_TAG'], f'_{region}_')
                    else:
                        output_name = output_path.stem + f'_{region}' + output_path.suffix
                else:
                    region = f'{output_region}+{region}'
                    output_name = output_path.name.replace(output_region, region)

                output_region = region
                output_path = output_path.with_name(output_name)

            # update suffix in output_path
            suffix = command.get_suffix()
            if suffix:
                output_path = output_path.with_suffix(suffix)

            # execute the command and obtain the command_string
            command_string = command.execute(job_path, input_path, output_path)

            # write the command_string into readme file
            readme.write(mask_paths(command_string) + '\n')

            # write the artefacts into the zipfile
            if command.artefacts:
                for artefact_path in command.artefacts:
                    if (job_path / artefact_path).is_file():
                        zip_file.write(job_path / artefact_path, artefact_path.name)

            # write the outputs into the zipfile and set the new input path
            if command.outputs:
                for output_path in command.outputs:
                    # set the new input path to the output path
                    input_path = output_path

                    if (job_path / output_path).is_file():
                        # write the output into the zipfile
                        zip_file.write(job_path / output_path, output_path.name)
                    else:
                        error_path = output_path.with_suffix('.txt')
                        error_path.write_text('Something went wrong with processing the input file.'
                                              ' Probably it is not using a global grid.')
                        zip_file.write(error_path, error_path.name)

        # update the current job and store progress
        job.meta['created_files'] += 1
        job.save_meta()

    # close and write readme file
    readme.close()
    zip_file.write(readme_path, readme_path.name)

    # close zip file
    zip_file.close()

    # delete temporary directory
    remove_job_path(job.id)

    # return True to indicate success
    return True
