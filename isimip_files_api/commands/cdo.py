import csv
import subprocess

from flask import current_app as app

from . import BaseCommand


class CdoCommand(BaseCommand):

    command = 'cdo'

    def execute(self, job_path, input_path, output_path):
        write_csv = (output_path.suffix == '.csv')

        # use the cdo bin from the config, NETCDF4_CLASSIC and compression
        cmd_args = [app.config['CDO_BIN'], '-f', 'nc4c', '-z', 'zip_5', '-L']

        # collect args from operations
        for operation in reversed(self.operations):
            operation.input_path = input_path
            operation.output_path = output_path
            cmd_args += operation.get_args()

        # add the input file
        cmd_args += [str(input_path)]

        # add the output file
        if not write_csv:
            cmd_args += [str(output_path)]

        # join the cmd_args and execute the the command
        cmd = ' '.join(cmd_args)
        app.logger.debug(cmd)

        output = subprocess.check_output(cmd_args, env={
            'CDI_VERSION_INFO': '0',
            'CDO_VERSION_INFO': '0',
            'CDO_HISTORY_INFO': '0'
        }, cwd=job_path)

        # write the subprocess output into a csv file
        if write_csv:
            with open(job_path / output_path, 'w', newline='') as fp:
                writer = csv.writer(fp, delimiter=',')
                for line in output.splitlines():
                    writer.writerow(line.decode().strip().split())

        # add the output path to the commands outputs
        self.outputs = [output_path]

        # return the command without the paths
        return cmd
