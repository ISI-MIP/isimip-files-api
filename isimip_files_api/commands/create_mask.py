import subprocess

from flask import current_app as app

from ..utils import mask_paths
from . import BaseCommand


class CreateMaskCommand(BaseCommand):

    command = 'create_mask'

    def execute(self, input_path, output_path):
        # use the ncks bin from the config
        cmd_args = [app.config['CREATE_MASK_BIN']]

        # add the arguments from the operations
        for operation in self.operations:
            operation.input_path = input_path
            operation.output_path = output_path
            cmd_args += operation.get_args()

        # add the input file and output file
        cmd_args += [str(input_path), str(output_path)]

        # join the cmd_args and execute the the command
        cmd = ' '.join(cmd_args)
        app.logger.debug(cmd)
        subprocess.check_output(cmd_args)

        # return the command without the paths
        return mask_paths(cmd)
