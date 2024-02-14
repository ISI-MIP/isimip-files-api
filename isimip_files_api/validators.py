from collections import defaultdict
from pathlib import Path

from flask import current_app as app

from .operations import OperationRegistry


def validate_data(data):
    errors = defaultdict(list)

    if (not data) or (data is None):
        errors['data'].append('No json data provided with POST')
    elif not isinstance(data, dict):
        errors['data'].append('Provided json data is malformatted')

    return errors


def validate_paths(data):
    errors = defaultdict(list)

    if not data.get('paths'):
        errors['paths'].append('This field is required.')
    elif not isinstance(data['paths'], list):
        errors['paths'].append('Provided json data is malformatted.')
    else:
        if len(data['paths']) > app.config['MAX_FILES']:
            errors['paths'].append('To many files match that dataset (max: {MAX_FILES}).'.format(**app.config))
        else:
            for path in data['paths']:
                # prevent tree traversal
                try:
                    input_path = Path(app.config['INPUT_PATH']).expanduser()
                    absolute_path = input_path / path
                    absolute_path.parent.resolve().relative_to(input_path.resolve())
                except ValueError:
                    errors['paths'].append(f'{path} is below the root path.')
                else:
                    # check if the file exists
                    if absolute_path.suffix not in ['.nc', '.nc4']:
                        errors['paths'].append(f'{path} is not a NetCDF file.')
                    # check if the file exists
                    elif not absolute_path.is_file():
                        errors['paths'].append(f'{path} was not found on the server.')

    return errors


def validate_operations(data):
    errors = defaultdict(list)

    if not data.get('operations'):
        errors['operations'].append('This field is required.')
    elif not isinstance(data['operations'], list):
        errors['operations'].append('Provided json data is malformatted.')
    elif len(data['operations']) > app.config['MAX_OPERATIONS']:
        errors['operations'].append('To many operations provided (max: {MAX_OPERATIONS}).'.format(**app.config))
    else:
        operation_registry = OperationRegistry()
        for index, operation_config in enumerate(data['operations']):
            if 'operation' in operation_config:
                operation = operation_registry.get(operation_config)
                if operation is None:
                    errors['operations'].append('operation "{operation}" was not found'.format(**operation_config))
                else:
                    operation_errors = operation.validate()
                    if operation_errors:
                        errors['operations'] += operation_errors
            else:
                errors['operations'].append(f'operation [{index}] does not have a "operation" key')

    if not errors and len(operation_registry.get_command_list(data['operations'])) > app.config['MAX_COMMANDS']:
        errors['operations'].append('Operations result in to many commands (max: {MAX_COMMANDS}).'.format(
            **app.config
        ))

    return errors


# # def validate_datasets(paths, args, errors):
# #     for path in paths:
# #         input_path = Path(app.config['INPUT_PATH']).expanduser()
# #         absolute_path = input_path / path
# #         with open_dataset(absolute_path) as ds:
# #             resolutions = app.config['RESOLUTION_TAGS'].get(args.get('task'))
# #             if not any(check_resolution(ds, resolution) for resolution in resolutions):
# #                 errors['paths'].append(f'{path} is not using the correct grid: {resolutions}.')
