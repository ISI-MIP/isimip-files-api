from . import BaseOperation, BBoxOperationMixin


class NcksOperation(BaseOperation):

    command = 'ncks'


class CutOutBBoxOperation(BBoxOperationMixin, NcksOperation):

    operation = 'cutout_bbox'

    def validate(self):
        return self.validate_bbox()

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
