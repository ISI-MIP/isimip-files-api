from rq import get_current_job

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
        'bbox': validate_bbox(data, errors),
        'country': validate_country(data, errors),
        'landonly': validate_landonly(data, errors)
    }
    if all([v is None for v in args.values()]):
        errors['args'] = 'Either bbox, country, or landonly needs to be provided'
    else:
        return args


def validate_bbox(data, errors):
    if 'bbox' in data:
        try:
            return [int(item) for item in data['bbox']]
        except ValueError:
            errors['bbox'] = 'bbox is not of the form [%d, %d, %d, %d]'
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


def validate_landonly(data, errors):
    if 'landonly' in data:
        if data['landonly'] is True:
            return True
        else:
            errors['landonly'] = 'Set {"landonly": true} to mask sea data'
    else:
        return None


def validate_dataset(ds):
    # check if the dataset is actual global gridded data
    if ds.dimensions['lat'].size == 360 or ds.dimensions['lon'].size == 720:
        return True
    else:
        # store the information that the job failed in job.meta
        job = get_current_job()
        job.meta['error'] = 'File is not global gridded data'
        job.save_meta()
        return False
