from .netcdf import open_dataset, check_halfdeg, check_30arcsec
from .settings import COUNTRYMASKS_COUNTRIES, INPUT_PATH, MAX_FILES, TASKS


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

    if len(data['paths']) > MAX_FILES:
        errors['paths'].append('To many files match that dataset (max: {}).'.format(MAX_FILES))
        return None

    for path in data['paths']:
        # prevent tree traversal
        try:
            absolute_path = INPUT_PATH / path
            absolute_path.parent.resolve().relative_to(INPUT_PATH.resolve())
        except ValueError:
            errors['paths'].append('{} is below the root path.'.format(path))

        # check if the file exists
        if not absolute_path.is_file():
            errors['paths'].append('{} was not found on the server.'.format(path))

        # check if the file exists
        if absolute_path.suffix not in ['.nc', '.nc4']:
            errors['paths'].append('{} is not a NetCDF file..'.format(path))

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
    if 'task' not in data or data['task'] not in TASKS:
        errors['task'] = 'task needs to be provided'
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

        if country.upper() not in COUNTRYMASKS_COUNTRIES:
            errors['country'] = 'country not in the list of supported countries (e.g. DEU)'

        return country
    else:
        return None


def validate_datasets(paths, args, errors):
    for path in paths:
        absolute_path = INPUT_PATH / path
        with open_dataset(absolute_path) as ds:
            if args.get('task') in ['cutout_bbox']:
                if not (check_halfdeg(ds) or check_30arcsec(ds)):
                    errors['paths'].append('{} is not using a 0.5 deg or 30 arcsec grid.'.format(path))
            else:
                if not check_halfdeg(ds):
                    errors['paths'].append('{} is not using a 0.5 deg grid.'.format(path))
