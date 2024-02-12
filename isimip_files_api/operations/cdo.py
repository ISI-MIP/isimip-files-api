from pathlib import Path

from flask import current_app as app

from . import BaseOperation, BBoxOperationMixin, CountryOperationMixin, PointOperationMixin


class CdoOperation(BaseOperation):

    agent = 'cdo'

    def get_command(self):
        return [app.config['CDO_BIN']]

    def get_cmd_args(self):
        return ['x', 'y']

    def get_env(self):
        return {
            'CDI_VERSION_INFO': '0',
            'CDO_VERSION_INFO': '0',
            'CDO_HISTORY_INFO': '0'
        }

    # def execute(*args, output_path=None):
    #     cmd_args = [app.config['CDO_BIN'], *list(args)]
    #     cmd = ' '.join(cmd_args)
    #     env =

    #     app.logger.debug(cmd)
    #     output = subprocess.check_output(cmd_args, env=env)

    #     if output_path:
    #         with open(output_path, 'w', newline='') as fp:
    #             writer = csv.writer(fp, delimiter=',')
    #             for line in output.splitlines():
    #                 writer.writerow(line.decode().strip().split())

    #     return mask_cmd(cmd)


class SelectBBoxOperation(BBoxOperationMixin, CdoOperation):

    specifier = 'select_bbox'

    def validate(self):
        return self.validate_bbox()

    def get_args(self):
        south, north, west, east = self.get_bbox()
        return [f'-sellonlatbox,{west:f},{east:f},{south:f},{north:f}']


class SelectCountryOperation(CountryOperationMixin, CdoOperation):

    specifier = 'select_country'

    def validate(self):
        return self.validate_country()

    def get_args(self):
        country = self.get_country()
        mask_path = str(Path(app.config['COUNTRYMASKS_FILE_PATH']).expanduser())
        return ['-ifthen', f'-selname,m_{country:3.3}', mask_path]


class SelectPointOperation(PointOperationMixin, CdoOperation):

    specifier = 'select_point'

    def validate(self):
        return self.validate_point()

    # def cmd_args(self):
    #     # cdo -s outputtab,date,value,nohead -selindexbox,IX,IX,IY,IY IFILE
    #     ix, iy = get_index(dataset_path, point)

    #     # add one since cdo is counting from 1!
    #     ix, iy = ix + 1, iy + 1

    #     return [f'-selindexbox,{ix:d},{ix:d},{iy:d},{iy:d}']


class MaskBBoxOperation(BBoxOperationMixin, CdoOperation):

    specifier = 'mask_bbox'

    def validate(self):
        return self.validate_bbox()

    def get_args(self):
        south, north, west, east = self.get_bbox()
        return [f'-masklonlatbox,{west:f},{east:f},{south:f},{north:f}']


class MaskCountryOperation(CountryOperationMixin, CdoOperation):

    specifier = 'mask_country'

    def validate(self):
        return self.validate_country()

    def get_args(self):
        country = self.get_country()
        mask_path = str(Path(app.config['COUNTRYMASKS_FILE_PATH']).expanduser())
        return [f'-selname,m_{country:3.3}', mask_path]


class MaskLandonlyOperation(CdoOperation):

    specifier = 'mask_landonly'

    def get_args(self):
        mask_path = str(Path(app.config['LANDSEAMASK_FILE_PATH']).expanduser())
        return ['-ifthen', mask_path]


class FldmeanOperation(CdoOperation):

    specifier = 'fldmean'

    def get_args(self):
        return ['-fldmean']


class OutputtabOperation(CdoOperation):

    specifier = 'outputtab'

    def get_args(self):
        return ['-s outputtab,date,value,nohead']
