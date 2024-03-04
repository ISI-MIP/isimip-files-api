from pathlib import Path

from flask import current_app as app

from ..netcdf import get_index
from . import BaseOperation, BBoxOperationMixin, CountryOperationMixin, MaskOperationMixin, PointOperationMixin


class CdoOperation(BaseOperation):

    command = 'cdo'


class SelectBBoxOperation(BBoxOperationMixin, CdoOperation):

    operation = 'select_bbox'

    def validate(self):
        return self.validate_bbox()

    def get_args(self):
        south, north, west, east = self.get_bbox()
        return [f'-sellonlatbox,{west:f},{east:f},{south:f},{north:f}']

    def get_region(self):
        south, north, west, east = self.get_bbox()
        return f'lat{south}to{north}lon{west}to{east}'


class SelectPointOperation(PointOperationMixin, CdoOperation):

    operation = 'select_point'

    def validate(self):
        return self.validate_point()

    def get_args(self):
        point = self.get_point()
        ix, iy = get_index(self.input_path, point)

        # add one since cdo is counting from 1!
        ix, iy = ix + 1, iy + 1

        return [f'-selindexbox,{ix:d},{ix:d},{iy:d},{iy:d}']

    def get_region(self):
        lat, lon = self.get_point()
        return f'lat{lat}lon{lon}'


class MaskBBoxOperation(BBoxOperationMixin, CdoOperation):

    operation = 'mask_bbox'

    def validate(self):
        return self.validate_bbox()

    def get_args(self):
        south, north, west, east = self.get_bbox()
        return [f'-masklonlatbox,{west:f},{east:f},{south:f},{north:f}']

    def get_region(self):
        south, north, west, east = self.get_bbox()
        return f'lat{south}to{north}lon{west}to{east}'


class MaskMaskOperation(MaskOperationMixin, CdoOperation):

    operation = 'mask_mask'

    def validate(self):
        errors = []
        errors += self.validate_var() or []
        errors += self.validate_mask() or []
        return errors

    def get_args(self):
        var = self.get_var()
        mask_path = self.get_mask_path()
        return ['-ifthen', f'-selname,{var}', str(mask_path)]

    def get_region(self):
        mask_path = self.get_mask_path()
        return mask_path.stem


class MaskCountryOperation(CountryOperationMixin, CdoOperation):

    operation = 'mask_country'

    def validate(self):
        return self.validate_country()

    def get_args(self):
        country = self.get_country()
        mask_path = str(Path(app.config['COUNTRYMASKS_FILE_PATH']).expanduser())
        return ['-ifthen', f'-selname,m_{country:3.3}', mask_path]

    def get_region(self):
        return self.get_country().lower()


class MaskLandonlyOperation(CdoOperation):

    operation = 'mask_landonly'

    def validate(self):
        pass

    def get_args(self):
        mask_path = str(Path(app.config['LANDSEAMASK_FILE_PATH']).expanduser())
        return ['-ifthen', mask_path]

    def get_region(self):
        return 'landonly'


class ComputeMeanOperation(CdoOperation):

    operation = 'compute_mean'

    def validate(self):
        pass

    def get_args(self):
        return ['-fldmean']


class OutputCsvOperation(CdoOperation):

    operation = 'output_csv'

    def validate(self):
        pass

    def get_args(self):
        return ['-s', 'outputtab,date,value,nohead']

    def get_suffix(self):
        return '.csv'
