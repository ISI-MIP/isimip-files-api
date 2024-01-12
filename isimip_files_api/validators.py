from pathlib import Path

from flask import current_app as app

from .netcdf import check_resolution, open_dataset


def validate_data(data, errors):
    # check if any data is provided
    if (not data) or (data is None):
        errors['data'] = 'No json data provided with POST'
    elif not isinstance(data, dict):
        errors['data'] = 'Provided json data is malformatted'
    else:
        paths = validate_paths(data, errors)
        args = validate_args(data, errors)
        return paths, args


def validate_paths(data, errors):
    # check if path is given
    if 'paths' not in data:
        errors['paths'].append('This field is required.')
        return None

    if len(data['paths']) > app.config['MAX_FILES']:
        errors['paths'].append('To many files match that dataset (max: {MAX_FILES}).'.format(**app.config))
        return None

    for path in data['paths']:
        # prevent tree traversal
        try:
            input_path = Path(app.config['INPUT_PATH']).expanduser()
            absolute_path = input_path / path
            absolute_path.parent.resolve().relative_to(input_path.resolve())
        except ValueError:
            errors['paths'].append(f'{path} is below the root path.')

        # check if the file exists
        if not absolute_path.is_file():
            errors['paths'].append(f'{path} was not found on the server.')

        # check if the file exists
        if absolute_path.suffix not in ['.nc', '.nc4']:
            errors['paths'].append(f'{path} is not a NetCDF file..')

    return data['paths']


def validate_args(data, errors):
    args = {
        'task': validate_task(data, errors),
        'bbox': validate_bbox(data, errors),
        'point': validate_point(data, errors),
        'country': validate_country(data, errors)
    }
    if args['task'] in ['select_country', 'mask_country'] and not args['country']:
            errors['args'] = 'country needs to be provided'
    elif args['task'] in ['cutout_bbox', 'mask_bbox', 'select_bbox'] and not args['bbox']:
            errors['args'] = 'bbox needs to be provided'
    elif args['task'] in ['select_point'] and not args['point']:
            errors['args'] = 'point needs to be provided'
    else:
        return args


def validate_task(data, errors):
    app.logger.info(data)
    if 'task' not in data:
        errors['task'] = 'task needs to be provided'
    elif data['task'] not in app.config['TASKS']:
        errors['task'] = "task '{task}' is not supported".format(**data)
    else:
        return data['task']


def validate_bbox(data, errors):
    if 'bbox' in data:
        try:
            return [float(data['bbox'][0]), float(data['bbox'][1]), float(data['bbox'][2]), float(data['bbox'][3])]
        except (ValueError, IndexError):
            errors['bbox'] = 'bbox is not of the form [%f, %f, %f, %f]'
    else:
        return None


def validate_point(data, errors):
    if 'point' in data:
        try:
            return [float(data['point'][0]), float(data['point'][1])]
        except (ValueError, IndexError):
            errors['bbox'] = 'bbox is not of the form [%f, %f]'
    else:
        return None


def validate_country(data, errors):
    if 'country' in data:
        country = data['country'].lower()

        if country.upper() not in app.config['COUNTRYMASKS_COUNTRIES']:
            errors['country'] = 'country not in the list of supported countries (e.g. DEU)'

        return country
    else:
        return None


def validate_datasets(paths, args, errors):
    for path in paths:
        input_path = Path(app.config['INPUT_PATH']).expanduser()
        absolute_path = input_path / path
        with open_dataset(absolute_path) as ds:
            resolutions = app.config['RESOLUTION_TAGS'].get(args.get('task'))
            if not any(check_resolution(ds, resolution) for resolution in resolutions):
                errors['paths'].append(f'{path} is not using the correct grid: {resolutions}.')
