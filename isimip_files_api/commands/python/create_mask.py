import subprocess
from pathlib import Path

from flask import current_app as app

from isimip_files_api.commands import BaseCommand


class CreateMaskCommand(BaseCommand):

    command = 'create_mask'

    perform_once = True
    max_operations = 1

    def execute(self, job_path, input_path, output_path):
        # use the ncks bin from the config
        cmd_args = [app.config['CREATE_MASK_BIN']]

        # add the arguments from the first operation
        shape_file, mask_file = self.operations[0].get_args()

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
