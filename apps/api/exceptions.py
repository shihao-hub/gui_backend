class ServiceUnavailableError(Exception):
    pass


class BadRequestError(Exception):
    # TODO: 待完善
    def __init__(self, data):
        self.data = data
