from .settings import COUNTRYMASKS_COUNTRIES, INPUT_PATH, MAX_FILES


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
        'country': validate_country(data, errors)
    }
    if args['task'] in ['mask_country'] and not args['country']:
            errors['args'] = 'country needs to be provided'
    elif args['task'] in ['cutout_bbox', 'mask_bbox'] and not args['bbox']:
            errors['args'] = 'bbox needs to be provided'
    else:
        return args


def validate_task(data, errors):
    if 'task' not in data or data['task'] not in ['cutout_bbox', 'mask_bbox', 'mask_country', 'mask_landonly']:
        errors['task'] = 'task needs to be provided'
    else:
        return data['task']


def validate_bbox(data, errors):
    if 'bbox' in data:
        try:
            return [float(item) for item in data['bbox']]
        except ValueError:
            errors['bbox'] = 'bbox is not of the form [%f, %f, %f, %f]'
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


def validate_dataset(ds):
    # check if the dataset is actual global gridded data
    if ds.dimensions['lat'].size == 360 or ds.dimensions['lon'].size == 720:
        return True
    else:
        return False
