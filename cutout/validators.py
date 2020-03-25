from pathlib import Path

from rq import get_current_job

from .settings import COUNTRYMASKS_COUNTRIES, INPUT_PATH


def validate_data(data, errors):
    # check if any data is provided
    if not data:
        errors['data'] = 'No json data provided with POST'

    return data


def validate_path(data, errors):
    # check if path is given
    if 'path' not in data:
        errors['path'] = 'This field is required'

    # construct file_path
    file_path = INPUT_PATH / data['path']

    # prevent tree traversal
    try:
        file_path.resolve().relative_to(INPUT_PATH.resolve())
    except ValueError:
        errors['path'] = 'File is below root path'

    # check if file exists
    if not file_path.is_file():
        errors['path'] = 'File not found'

    return Path(data['path'])


def validate_bbox(data, errors):
    try:
        return [float(item) for item in data['bbox']]
    except ValueError:
        errors['bbox'] = 'bbox is not of the form [%f, %f, %f, %f]'


def validate_country(data, errors):
    country = data['country'].lower()

    if country.upper() not in COUNTRYMASKS_COUNTRIES:
        errors['country'] = 'country not in the list of supported countries (e.g. DEU, )'

    return country


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
