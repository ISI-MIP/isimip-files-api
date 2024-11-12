class OperationError(RuntimeError):

    def __init__(self, e, message=''):
        super().__init__(e)
        self.message = message
