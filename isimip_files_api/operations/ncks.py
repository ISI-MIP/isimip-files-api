import subprocess

from flask import current_app as app

from isimip_files_api.netcdf import get_resolution
from isimip_files_api.operations import BaseOperation, BBoxOperationMixin, PointOperationMixin
from isimip_files_api.utils import get_input_path


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

    def validate_resolution(self, path):
        input_resolution = get_resolution(get_input_path() / path)
        config_resolution = app.config['NCKS_MAX_RESOLUTION']

        if input_resolution[0] > config_resolution[0] or input_resolution[1] > config_resolution[1]:
            return [f'resolution of {path} {input_resolution} is to high {config_resolution}'
                    f' for operation "{self.operation}"']


class CutOutBBoxOperation(BBoxOperationMixin, NcksOperation):

    operation = 'cutout_bbox'

    def get_args(self):
        west, east, south, north = self.get_bbox()
        return [
            '-h',                              # omit history
            '-d', f'lon,{west:f},{east:f}',    # longitude
            '-d', f'lat,{south:f},{north:f}',  # latitude
        ]


class CutOutPointOperation(PointOperationMixin, NcksOperation):

    operation = 'cutout_point'

    def get_args(self):
        lat, lon = self.get_point()
        return [
            '-h',                  # omit history
            '-d', f'lon,{lon:f}',  # longitude
            '-d', f'lat,{lat:f}',  # latitude
        ]
