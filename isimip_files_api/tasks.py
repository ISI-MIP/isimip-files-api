import json
from pathlib import Path

from flask import current_app as app

from rq import get_current_job

from .exceptions import OperationError
from .operations import OperationRegistry
from .utils import get_input_path, get_job_path, get_zip_file, mask_paths, remove_job_path


def run_task(paths, operations):
    # get current job and init metadata
    job = get_current_job()
    job.meta['created_files'] = 0
    job.meta['total_files'] = len(paths)
    job.meta['errors'] = {}
    job.save_meta()

    # get the temporary directory
    job_path = get_job_path(job.id)

    # create the output zip file
    zip_file = get_zip_file(job.id)

    # open readme
    readme_path = job_path / 'README.txt'
    readme = readme_path.open('w')

    # get the list of operation objects to perform
    operation_registry = OperationRegistry()
    operation_list = [operation_registry.get(config) for config in operations]

    for path in paths:
        input_path = get_input_path() / path
        output_path = Path(input_path.name)
        output_region = None

        for operation in operation_list:
            # check if the operation should only be performed once and skip all but the first loop iteration
            if operation.perform_once and path != paths[0]:
                continue

            # validate the resolution and break if an error occures
            resolution_error = operation.validate_resolution(path)
            if resolution_error:
                job.meta['errors'][input_path.name] = resolution_error
                job.save_meta()
                break

            # update region tag in output_path
            region = operation.get_region()
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
            suffix = operation.get_suffix()
            if suffix:
                output_path = output_path.with_suffix(suffix)

            # execute the command and obtain the command_string
            try:
                command_string = operation.execute(job_path, input_path, output_path)
            except OperationError as e:
                command_error = str(e.message)
                job.meta['errors'][path.name] = command_error
                job.save_meta()
                break

            # write the command_string into readme file
            readme.write(mask_paths(command_string) + '\n')

            # write the artefacts into the zipfile
            if operation.artefacts:
                for artefact_path in operation.artefacts:
                    if (job_path / artefact_path).is_file():
                        zip_file.write(job_path / artefact_path, artefact_path.name)

            # write the outputs into the zipfile and set the new input path
            if operation.outputs:
                for output in operation.outputs:
                    # set the new input path to the output path
                    output_path = job_path / output
                    input_path = output_path

                    if output_path.is_file():
                        # write the output into the zipfile
                        zip_file.write(output_path, output_path.name)
                    else:
                        error_path = output_path.with_suffix('.error.txt')
                        error_path.write_text('Something went wrong with processing the input file.'
                                              ' Probably it is not using a global grid.')
                        zip_file.write(error_path, error_path.name)

        # update the current job and store progress
        job.meta['created_files'] += 1
        job.save_meta()

    # close and write readme file
    if readme.tell() == 0:
        # nothing was written to the readme
        readme.close()
    else:
        readme.seek(0)
        readme.write('The following commands were used to create the files in this container:\n\n')
        readme.close()
        zip_file.write(readme_path, readme_path.name)

    # open readme
    if job.meta['errors']:
        errors_path = job_path / 'errors.json'
        errors_path.write_text(json.dumps(job.meta['errors'], indent=2))
        zip_file.write(errors_path, errors_path.name)

    # close zip file
    zip_file.close()

    # delete temporary directory
    remove_job_path(job.id)

    # return True to indicate success
    return True
