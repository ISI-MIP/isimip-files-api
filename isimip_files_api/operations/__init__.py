import re
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
        current_command = None
        for index, operation_config in enumerate(operations):
            operation = self.get(operation_config)

            # add a new command, if
            # * its the first operation
            # * the operation has a different command than the previous one
            # * the command reached its limit of operations
            if (
                current_command is None or
                current_command.command != operation.command or
                (
                    current_command.max_operations is not None and
                    len(current_command.operations) >= current_command.max_operations
                )
            ):
                current_command = command_registry.get(operation.command)
                commands.append(current_command)

            current_command.operations.append(operation)

        return commands


class BaseOperation:

    def __init__(self, config):
        self.config = config

    def validate(self):
        raise NotImplementedError

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
            if not re.match(r'^[A-Za-z0-9-.]*$', self.config['mask']):
                return ['only letters, numbers, hyphens, and periods are permitted in "mask"'
                        f' for operation "{self.operation}"']
            elif re.search(r'\.{2}', self.config['mask']):
                return [f'consecutive periods are not permitted in "mask" for operation "{self.operation}"']
        else:
            return [f'mask is missing for operation "{self.operation}"']
