import subprocess


def cutout_bbox(dataset_path, output_path, bbox):
    south, north, west, east = bbox
    cmd = [
        'ncks',
        '-O',                                        # overwrite
        '-d', 'lat,{:g},{:g}'.format(south, north),  # longitude
        '-d', 'lon,{:g},{:g}'.format(west, east),  # latitude
        str(dataset_path),                           # input
        str(output_path)                             # output
    ]
    subprocess.check_call(cmd)
