from lib.esystem.exceptions import  EException

class PyNetException(EException):
    def __init__(self, message: str, cause: Exception = None):
        self.__message = message
        self.__cause = cause