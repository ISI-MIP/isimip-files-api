import subprocess

from flask import current_app as app

from . import BaseCommand


class NcksCommand(BaseCommand):

    command = 'ncks'

    def execute(self, job_path, input_path, output_path):
        # use the ncks bin from the config
        cmd_args = [app.config['NCKS_BIN']]

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
        subprocess.check_call(cmd_args, cwd=job_path)

        # add the output path to the commands outputs
        self.outputs = [output_path]

        # return the command without the paths
        return cmd
