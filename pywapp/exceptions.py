class GetDataError(Exception):
    def __init__(self, message: str):
        super().__init__(message)

class NotLoggedInError(Exception):
    def __init__(self, message: str):
        super().__init__(message)

class InvalidEventError(Exception):
    def __init__(self, message: str):
        super().__init__(message)

class StaleElementReferenceError(Exception):
    def __init__(self, message: str):
        super().__init__(message)

class UnknownError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
