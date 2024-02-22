from flask import current_app as app

from ..utils import import_class


class CommandRegistry:

    def __init__(self):
        self.commands = {}
        for python_path in app.config['COMMANDS']:
            command_class = import_class(python_path)
            self.commands[command_class.command] = command_class

    def get(self, command):
        if command in self.commands:
            return self.commands[command]()
        else:
            raise RuntimeError(f'Command "{command}" not found in CommandRegistry.')


class BaseCommand:

    def __init__(self):
        self.operations = []

    def execute(self, input_path, output_path):
        raise NotImplementedError


    def get_suffix(self):
        # loop over operations and take the first one
        for operation in self.operations:
            suffix = operation.get_suffix()
            if suffix is not None:
                return suffix

    def get_region(self):
        # loop over operations concat the regions with a hyphen
        regions = []
        for operation in self.operations:
            region = operation.get_region()
            if region is not None:
                regions.append(region)
        return '-'.join(regions)
