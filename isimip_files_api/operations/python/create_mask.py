from isimip_files_api.operations import BaseOperation, MaskOperationMixin


class CreateMaskOperation(MaskOperationMixin, BaseOperation):

    command = 'create_mask'
    operation = 'create_mask'

    def validate(self):
        errors = []
        errors += self.validate_shape() or []
        errors += self.validate_mask() or []
        return errors

    def validate_shape(self):
        if 'shape' not in self.config:
            return [f'shape is missing for operation "{self.operation}"']

    def validate_uploads(self, uploads):
        if 'shape' in self.config:
            shape = self.config['shape']
            if not uploads.get(shape):
                return [f'File "{shape}" for operation "{self.operation}" is not part of the uploads']

    def get_args(self):
        return [
            self.config.get('shape'),
            self.config.get('mask')
        ]
