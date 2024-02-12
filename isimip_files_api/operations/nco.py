
from . import BaseOperation, BBoxOperationMixin


class NcoOperation(BaseOperation):
    pass

    # def execute(*args, output_path=None):
    #     cmd_args = [app.config['NCKS_BIN'], *list(args)]
    #     cmd = ' '.join(cmd_args)

    #     logging.debug(cmd)
    #     subprocess.check_output(cmd_args)

    #     return mask_cmd(cmd)


class CutoutBBoxOperation(BBoxOperationMixin, NcoOperation):

    specifier = 'cutout_bbox'

    def validate(self):
        return self.validate_bbox()
