import base64
import binascii
import io
import json
import zipfile
from pathlib import Path

from . import BaseOperation


class CreateMaskOperation(BaseOperation):

    command = 'create_mask'
    operation = 'create_mask'

    def validate(self):
        if 'shapefile' in self.config and 'geojson' in self.config:
            return [f'shapefile and geojson and mutually exclusive for operation "{self.operation}"']

        elif 'shapefile' in self.config:
            try:
                shapefile_stream = io.BytesIO(base64.b64decode(self.config['shapefile']))

                try:
                    with zipfile.ZipFile(shapefile_stream) as z:
                        for file_name in z.namelist():
                            if Path(file_name).suffix not in [
                                '.shp', '.dbf', '.shx', '.prj', '.sbn', '.sbx', '.fbn', '.fbx',
                                '.ain', '.aih', '.ixs', '.mxs', '.atx', '.shp.xml', '.cpg', '.qix'
                            ]:
                                return [f'shapefile is not a valid shape file for operation "{self.operation}"']
                except zipfile.BadZipFile:
                    return [f'shapefile is a valid zip file for operation "{self.operation}"']

            except binascii.Error:
                return [f'shapefile is not a valid base64 stream for operation "{self.operation}"']

        elif 'geojson' in self.config:
            try:
                json.loads(self.config['geojson'])
            except json.decoder.JSONDecodeError:
                return [f'geojson is not a valid json for operation "{self.operation}"']

        else:
            return [f'shapefile or geojson is missing for operation "{self.operation}"']

    def get_args(self):
        south, north, west, east = self.get_bbox()
        return [f'-sellonlatbox,{west:f},{east:f},{south:f},{north:f}']

    def get_region(self):
        south, north, west, east = self.get_bbox()
        return f'lat{south}to{north}lon{west}to{east}'
