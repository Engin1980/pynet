class EException(Exception):
    def __init__(self, message: str, cause: Exception = None):
        self.__message = message
        self.__cause = cause

    @property
    def cause(self):
        return self.__cause

    @property
    def message(self):
        return self.__message


class AppException(EException):
    def __init__(self, message: str, cause: Exception = None):
        super().__init__(message, cause)
