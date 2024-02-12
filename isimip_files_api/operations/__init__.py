from flask import current_app as app

from ..utils import import_class


class OperationRegistry:

    def __init__(self):
        from flask import current_app as app

        self.operations = {}
        for python_path in app.config['OPERATIONS']:
            operation_class = import_class(python_path)
            self.operations[operation_class.specifier] = operation_class

    def get(self, config):
        if 'specifier' in config and config['specifier'] in self.operations:
            return self.operations[config['specifier']](config)


class BaseOperation:

    def __init__(self, config):
        self.config = config

    def validate(self):
        pass


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
                self.get_bbox()
            except (ValueError, IndexError):
                return ['bbox is not of the form [%f, %f, %f, %f]']
        else:
            return [f'bbox is missing for operation "{self.specifier}"']


class PointOperationMixin:

    def get_point(self):
        return (
            float(self.config['point'][0]),
            float(self.config['point'][1])
        )

    def validate_point(self):
        if 'point' in self.config:
            try:
                self.get_point()
            except (ValueError, IndexError):
                return ['bbox is not of the form [%f, %f]']
        else:
            return [f'point is missing for operation "{self.specifier}"']


class CountryOperationMixin:

    def get_country(self):
        return self.config['country'].upper()

    def validate_country(self):
        if 'country' in self.config:
            if self.get_country() not in app.config['COUNTRYMASKS_COUNTRIES']:
                return ['country not in the list of supported countries (e.g. DEU)']
        else:
            return [f'country is missing for operation "{self.specifier}"']
