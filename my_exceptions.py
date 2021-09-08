class UserExists(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)


class AuthError(Exception):
    pass


class TooManyPhotos(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)
