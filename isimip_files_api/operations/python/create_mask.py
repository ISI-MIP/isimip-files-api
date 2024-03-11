import subprocess
from pathlib import Path

from flask import current_app as app

from isimip_files_api.operations import BaseOperation, MaskOperationMixin


class CreateMaskOperation(MaskOperationMixin, BaseOperation):

    operation = 'create_mask'
    perform_once = True

    def execute(self, job_path, input_path, output_path):
        # use the ncks bin from the config
        cmd_args = [app.config['CREATE_MASK_BIN']]

        # add the arguments from the operation
        shape_file, mask_file = self.get_args()

        # add the arguments to cmd_args
        cmd_args += [shape_file, mask_file]

        # join the cmd_args and execute the the command
        cmd = ' '.join(cmd_args)
        app.logger.debug(cmd)
        subprocess.check_call(cmd_args, cwd=job_path)

        # add the input and the output path of the command to the commands artefacts
        self.artefacts = [Path(shape_file), Path(mask_file)]

        # return the command without the paths
        return cmd

    def validate_shape(self):
        if 'shape' not in self.config:
            return [f'shape is missing for operation "{self.operation}"']

    def validate_uploads(self, uploads):
        if 'shape' in self.config:
            shape = self.config['shape']
            if not uploads.get(shape):
                return [f'File "{shape}" for operation "{self.operation}" is not part of the uploads']

    def get_args(self):
        return [
            self.config.get('shape'),
            self.config.get('mask')
        ]
