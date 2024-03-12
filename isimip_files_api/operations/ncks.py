import subprocess

from flask import current_app as app

from isimip_files_api.operations import BaseOperation, BBoxOperationMixin


class NcksOperation(BaseOperation):

    def execute(self, job_path, input_path, output_path):
        # use the ncks bin from the config
        cmd_args = [app.config['NCKS_BIN']]

        # add the arguments from the operations
        cmd_args += self.get_args()

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


class CutOutBBoxOperation(BBoxOperationMixin, NcksOperation):

    operation = 'cutout_bbox'

    def get_args(self):
        south, north, west, east = self.get_bbox()
        return [
            '-h',                              # omit history
            '-d', f'lat,{south:f},{north:f}',  # longitude
            '-d', f'lon,{west:f},{east:f}',    # latitude
        ]

    def get_region(self):
        south, north, west, east = self.get_bbox()
        return f'lat{south}to{north}lon{west}to{east}'
