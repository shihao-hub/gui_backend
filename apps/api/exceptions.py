class ServiceUnavailableError(Exception):
    pass


class BadRequestError(Exception):
    # TODO: 待完善
    def __init__(self, message, data=None):
        super().__init__(message)
        self.data = data
