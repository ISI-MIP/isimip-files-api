import base64
import binascii
import io
import json
import zipfile
from pathlib import Path

from flask import current_app as app

from ..commands import CommandRegistry
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

    def get_command_list(self, operations):
        commands = []

        command_registry = CommandRegistry()
        for index, operation_config in enumerate(operations):
            operation = self.get(operation_config)
            if not commands or commands[-1].command != operation.command:
                commands.append(command_registry.get(operation.command))
            commands[-1].operations.append(operation)

        return commands


class BaseOperation:

    def __init__(self, config):
        self.config = config

    def validate(self):
        raise NotImplementedError

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
                self.get_bbox()
            except (ValueError, IndexError):
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
                self.get_point()
            except (ValueError, IndexError):
                return [f'point is not of the form [%f, %f] for operation "{self.operation}"']
        else:
            return [f'point is missing for operation "{self.operation}"']


class CountryOperationMixin:

    def get_country(self):
        return self.config['country'].upper()

    def validate_country(self):
        if 'country' in self.config:
            if self.get_country() not in app.config['COUNTRYMASKS_COUNTRIES']:
                return [f'country not in the list of supported countries (e.g. deu) for operation "{self.operation}"']
        else:
            return [f'country is missing for operation "{self.operation}"']


class ShapeOperationMixin:

    def validate_shape(self):
        if 'shapefile' in self.config and 'geojson' in self.config:
            return [f'shapefile and geojson and mutually exclusive for operation "{self.operation}"']

        elif 'shapefile' in self.config:
            try:
                shapefile_stream = io.BytesIO(base64.b64decode(self.config['shapefile']))

                try:
                    with zipfile.ZipFile(shapefile_stream) as z:
                        for file_name in z.namelist():
                            if Path(file_name).suffix not in ['.dbf', '.prj', '.shp', '.shx']:
                                return [f'shapefile is not a valid shape file for operation "{self.operation}"']
                except zipfile.BadZipFile:
                    return [f'shapefile is a valid zip file for operation "{self.operation}"']

            except binascii.Error:
                return [f'shapefile is not a valid base64 stream for operation "{self.operation}"']

        elif 'geojson' in self.config:
            try:
                json.loads(self.config['geojson'])
            except json.decoder.JSONDecodeError:
                return [f'geojson is not a valid json for operation "{self.operation}"']

        else:
            return [f'shapefile or geojson is missing for operation "{self.operation}"']
