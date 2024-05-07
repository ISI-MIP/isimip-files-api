import csv
import subprocess
from pathlib import Path

from flask import current_app as app

from isimip_files_api.netcdf import get_index, get_resolution
from isimip_files_api.operations import (
    BaseOperation,
    BBoxOperationMixin,
    ComputeMeanMixin,
    CountryOperationMixin,
    MaskOperationMixin,
    OutputCsvMixin,
    PointOperationMixin,
)
from isimip_files_api.utils import get_input_path


class CdoOperation(BaseOperation):

    def execute(self, job_path, input_path, output_path):
        # store the input_path in the instance
        self.input_path = input_path

        # use the cdo bin from the config
        cmd_args = [app.config['CDO_BIN']]

        if self.config.get('write_tab') or self.config.get('output_csv'):
            cmd_args += ['-s', 'outputtab,date,value,nohead']
        else:
            # create NETCDF4_CLASSIC and add compression
            cmd_args += ['-f', 'nc4c', '-z', 'zip_5', '-L']

        if self.config.get('compute_mean'):
            cmd_args += ['-fldmean']

        # get args from operation
        cmd_args += self.get_args()

        # add the input file
        cmd_args += [str(input_path)]

        # add the output file
        if not (self.config.get('output_tab') or self.config.get('output_csv')):
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
        if self.config.get('output_csv'):
            with open(job_path / output_path, 'w', newline='') as fp:
                writer = csv.writer(fp, delimiter=',')
                for line in output.splitlines():
                    writer.writerow(line.decode().strip().split())

        # add the output path to the commands outputs
        self.outputs = [output_path]

        # return the command without the paths
        return cmd

    def validate_resolution(self, path):
        input_resolution = get_resolution(get_input_path() / path)
        config_resolution = app.config['CDO_MAX_RESOLUTION']

        if input_resolution[0] > config_resolution[0] or input_resolution[1] > config_resolution[1]:
            return [f'resolution of {path} {input_resolution} is to high {config_resolution}'
                    f' for operation "{self.operation}"']


class SelectBBoxOperation(OutputCsvMixin, ComputeMeanMixin, BBoxOperationMixin, CdoOperation):

    operation = 'select_bbox'

    def get_args(self):
        west, east, south, north = self.get_bbox()
        return [f'-sellonlatbox,{west:f},{east:f},{south:f},{north:f}']

    def get_region(self):
        west, east, south, north = self.get_bbox()
        return f'lon{west}to{east}lat{south}to{north}'


class SelectPointOperation(OutputCsvMixin, PointOperationMixin, CdoOperation):

    operation = 'select_point'

    def get_args(self):
        point = self.get_point()
        ix, iy = get_index(self.input_path, point)

        # add one since cdo is counting from 1!
        ix, iy = ix + 1, iy + 1

        return [f'-selindexbox,{ix:d},{ix:d},{iy:d},{iy:d}']

    def get_region(self):
        lat, lon = self.get_point()
        return f'lon{lon}lat{lat}'


class MaskBBoxOperation(OutputCsvMixin, ComputeMeanMixin, BBoxOperationMixin, CdoOperation):

    operation = 'mask_bbox'

    def get_args(self):
        west, east, south, north = self.get_bbox()
        return [f'-sellonlatbox,{west:f},{east:f},{south:f},{north:f}']

    def get_region(self):
        west, east, south, north = self.get_bbox()
        return f'lon{west}to{east}lat{south}to{north}'


class MaskMaskOperation(OutputCsvMixin, ComputeMeanMixin, MaskOperationMixin, CdoOperation):

    operation = 'mask_mask'

    def get_args(self):
        var = self.get_var()
        mask_path = self.get_mask_path()
        return ['-ifthen', f'-selname,{var}', str(mask_path)]

    def get_region(self):
        mask_path = self.get_mask_path()
        return mask_path.stem


class MaskCountryOperation(OutputCsvMixin, ComputeMeanMixin, CountryOperationMixin, CdoOperation):

    operation = 'mask_country'

    def get_args(self):
        country = self.get_country()
        mask_path = str(Path(app.config['COUNTRYMASKS_FILE_PATH']).expanduser())
        return ['-ifthen', f'-selname,m_{country:3.3}', mask_path]

    def get_region(self):
        return self.get_country().lower()

    def validate_resolution(self, path):
        input_resolution = get_resolution(get_input_path() / path)
        mask_resolution = get_resolution(Path(app.config['COUNTRYMASKS_FILE_PATH']).expanduser())

        if input_resolution != mask_resolution:
            return [f'resolution of {path} {input_resolution} does not match mask resolution {mask_resolution}'
                    f' for operation "{self.operation}"']


class MaskLandonlyOperation(CdoOperation):

    operation = 'mask_landonly'

    def get_args(self):
        mask_path = str(Path(app.config['LANDSEAMASK_FILE_PATH']).expanduser())
        return ['-ifthen', mask_path]

    def get_region(self):
        return 'landonly'

    def validate_resolution(self, path):
        input_resolution = get_resolution(get_input_path() / path)
        mask_resolution = get_resolution(Path(app.config['LANDSEAMASK_FILE_PATH']).expanduser())

        if input_resolution != mask_resolution:
            return [f'resolution of {path} {input_resolution} does not match mask resolution {mask_resolution}'
                    f' for operation "{self.operation}"']
