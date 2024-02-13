import shutil
from pathlib import Path
from tempfile import mkdtemp
from zipfile import ZipFile

from flask import current_app as app

from rq import get_current_job

from .commands import CommandsRegistry
from .operations import OperationRegistry
from .utils import get_zip_file_name


def run_task(paths, operations):
    # get current job and init metadata
    job = get_current_job()
    job.meta['created_files'] = 0
    job.meta['total_files'] = len(paths)
    job.save_meta()

    # create output paths
    zip_path = Path(app.config['OUTPUT_PATH']).expanduser() / get_zip_file_name(job.id)
    zip_path.parent.mkdir(parents=True, exist_ok=True)

    # create a temporary directory
    tmp_path = Path(mkdtemp(prefix=app.config['OUTPUT_PREFIX']))

    # open zipfile
    z = ZipFile(zip_path, 'w')

    # open readme
    readme_path = tmp_path / 'README.txt'
    readme = readme_path.open('w')
    readme.write('The following commands were used to create the files in this container:\n\n')

    commands = []
    commands_registry = CommandsRegistry()
    operation_registry = OperationRegistry()
    for index, operation_config in enumerate(operations):
        operation = operation_registry.get(operation_config)
        if not commands or commands[-1].command != operation.command:
            commands.append(commands_registry.get(operation.command))
        commands[-1].operations.append(operation)

    for path in paths:
        input_path = output_path = output_region = None

        for command in commands:
            if output_path is None:
                input_path = Path(app.config['INPUT_PATH']).expanduser() / path
                output_path = tmp_path / input_path.name
            else:
                input_path = output_path

            region = command.get_region()
            if region is not None:
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

            suffix = command.get_suffix()
            if suffix is not None:
                output_path = output_path.with_suffix(suffix)

            # execute the command and obtain the command_string
            command_string = command.execute(input_path, output_path)

            # write the command_string into readme file
            readme.write(command_string + '\n')

        if output_path.is_file():
            z.write(output_path, output_path.name)
            print(output_path, output_path.name)
        else:
            error_path = Path(tmp_path).with_suffix('.txt')
            error_path.write_text('Something went wrong with processing the input file.'
                                  ' Probably it is not using a global grid.')
            z.write(error_path, error_path.name)

        # update the current job and store progress
        job.meta['created_files'] += 1
        job.save_meta()

    # close and write readme file
    readme.close()
    z.write(readme_path, readme_path.name)

    # close zip file
    z.close()

    # delete temporary directory
    shutil.rmtree(tmp_path)

    # return True to indicate success
    return True
