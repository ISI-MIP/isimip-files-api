import re
from pathlib import Path

from flask import current_app as app

from ..utils import import_class


class OperationRegistry:

    def __init__(self):
        self.operations = {}
        for python_path in app.config['OPERATIONS']:
            operation_class = import_class(python_path)
            self.operations[operation_class.operation] = operation_class

    def get(self, config):
        if 'operation' in config and config['operation'] in self.operations:
            return self.operations[config['operation']](config)


class BaseOperation:

    perform_once = False

    def __init__(self, config):
        self.config = config
        self.artefacts = []
        self.output = None

    def validate_config(self):
        # gather all methods in the class which start with "validate_", but not "validate_uploads"
        method_names = [
            method_name for method_name in dir(self)
            if all([
                callable(getattr(self, method_name)),
                method_name.startswith('validate_'),
                method_name not in [
                    'validate_config',
                    'validate_resolution',
                    'validate_uploads'
                ]
            ])
        ]

        # loop over validation_methods and collect errors
        errors = []
        for method_name in method_names:
            errors += getattr(self, method_name)() or []
        return errors

    def validate_resolution(self, uploads):
        pass

    def validate_uploads(self, uploads):
        pass

    def get_args(self):
        raise NotImplementedError

    def get_suffix(self):
        return None

    def get_region(self):
        return None


class BBoxOperationMixin:

    def get_bbox(self):
        return (
            float(self.config['bbox'][0]),
            float(self.config['bbox'][1]),
            float(self.config['bbox'][2]),
            float(self.config['bbox'][3])
        )

    def validate_bbox(self):
        if 'bbox' in self.config:
            try:
                west, east, south, north = self.get_bbox()
                if west > 180.0:
                    return [f'west longitude is > 180 in bbox for operation "{self.operation}"']
                if west < -180.0:
                    return [f'west longitude is < -180 in bbox for operation "{self.operation}"']
                if east > 180.0:
                    return [f'east longitude is > 180 in bbox for operation "{self.operation}"']
                if east < -180.0:
                    return [f'east longitude is < -180 in bbox for operation "{self.operation}"']
                if south > 90.0:
                    return [f'south latitude is > 90 in bbox for operation "{self.operation}"']
                if south < -90.0:
                    return [f'south latitude is < -90 in bbox for operation "{self.operation}"']
                if north > 90.0:
                    return [f'north latitude is > 90 in bbox for operation "{self.operation}"']
                if north < -90.0:
                    return [f'north latitude is < -90 in bbox for operation "{self.operation}"']
            except (ValueError, IndexError, TypeError):
                return [f'bbox is not of the form [%f, %f, %f, %f] for operation "{self.operation}"']
        else:
            return [f'bbox is missing for operation "{self.operation}"']


class PointOperationMixin:

    def get_point(self):
        return (
            float(self.config['point'][0]),
            float(self.config['point'][1])
        )

    def validate_point(self):
        if 'point' in self.config:
            try:
                lon, lat = self.get_point()
                if lon > 180.0:
                    return [f'longitude is > 180 in point for operation "{self.operation}"']
                if lon < -180.0:
                    return [f'longitude is < -180 in point for operation "{self.operation}"']
                if lat > 90.0:
                    return [f'latitude is > 90 in point for operation "{self.operation}"']
                if lat < -90.0:
                    return [f'latitude is < -90 in point for operation "{self.operation}"']
            except (ValueError, IndexError, TypeError):
                return [f'point is not of the form [%f, %f] for operation "{self.operation}"']
        else:
            return [f'point is missing for operation "{self.operation}"']


class CountryOperationMixin:

    def get_country(self):
        return self.config['country'].upper()

    def get_mask_path(self):
        return Path(app.config['COUNTRYMASKS_FILE_PATH']).expanduser().resolve()

    def validate_country(self):
        if 'country' in self.config:
            if self.get_country() not in app.config['COUNTRYMASKS_COUNTRIES']:
                return [f'country not in the list of supported countries (e.g. deu) for operation "{self.operation}"']
        else:
            return [f'country is missing for operation "{self.operation}"']


class MaskOperationMixin:

    def get_var(self):
        return self.config.get('var', 'm_0')

    def get_mask_path(self):
        return Path(self.config.get('mask'))

    def validate_var(self):
        if 'var' in self.config:
            if not re.match(r'^[A-Za-z0-9_]*$', self.config['var']):
                return [f'only letters, numbers, underscores are permitted in "var" for operation "{self.operation}"']

    def validate_mask(self):
        if 'mask' in self.config:
            if not re.match(r'^[A-Za-z0-9-_.]*$', self.config['mask']):
                return ['only letters, numbers, hyphens, underscores, and periods are permitted in "mask"'
                        f' for operation "{self.operation}"']
            elif re.search(r'\.{2}', self.config['mask']):
                return [f'consecutive periods are not permitted in "mask" for operation "{self.operation}"']
        else:
            return [f'mask is missing for operation "{self.operation}"']


class ComputeMeanMixin:

    def validate_compute_mean(self):
        if 'compute_mean' in self.config:
            if self.config['compute_mean'] not in [True, False]:
                return [f'only true or false are permitted in "compute_mean" for operation "{self.operation}"']


class OutputCsvMixin:

    def validate_output_csv(self):
        if 'output_csv' in self.config:
            if self.config['output_csv'] not in [True, False]:
                return [f'only true or false are permitted in "output_csv" for operation "{self.operation}"']

    def get_suffix(self):
        if self.config.get('output_csv'):
            return '.csv'
