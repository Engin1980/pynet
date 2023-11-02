from enum import Enum, IntEnum
from Lib.easserting import EAssert
from Lib.events import Event
from Lib.elogging import LogLevel
import struct
from typing import List, Optional, Callable

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


class PyNetException(EException):
    def __init__(self, message: str, cause: Exception = None):
        self.__message = message
        self.__cause = cause


class BitUtilities:

    @staticmethod
    def str_to_bytes(value: str) -> bytes:
        ret = value.encode("UTF-8")
        return ret

    @staticmethod
    def bytes_to_str(value: bytes) -> str:
        ret = value.decode("UTF-8")
        return ret

    @staticmethod
    def float_to_bytes(value: float) -> bytes:
        ret = struct.pack('<d', value)
        return ret

    @staticmethod
    def bytes_to_float(value: bytes) -> float:
        ret = struct.unpack('<d', value)
        ret = ret[0]
        return ret

    @staticmethod
    def int_to_bytes(value: int, byteorder='little') -> bytes:
        ret = value.to_bytes(4, byteorder, signed=True)
        return ret

    @staticmethod
    def bytes_to_int(value: bytes, byteorder='little', signed=True):
        ret = int.from_bytes(value, byteorder=byteorder, signed=signed)
        return ret

    @staticmethod
    def split_bytes_to_blocks(data, block_length):
        EAssert.is_true(len(data) % block_length == 0,
                        f"Data-block of length {len(data)} cannot be divided by {block_length} without left-overs.")
        ret = []
        istart = 0
        cnt = len(data)
        while istart < cnt:
            iend = istart + block_length
            blk = data[istart:iend]
            ret.append(blk)
            istart = iend
        return ret

    @staticmethod
    def bytes_to_bool(value: bytes):
        ret = False if value[0] == 0 else True
        return ret

    @staticmethod
    def bool_to_bytes(value: bool) -> bytes:
        ret = bytes([1]) if value else bytes([0])
        return ret

    @staticmethod
    def int_length():
        return 4

    @staticmethod
    def float_length():
        return 8

    @staticmethod
    def bool_length():
        return 1


class EList:
    def __init__(self, data: [] = None):
        self.__inner = data if data is not None else []

    def append(self, item):
        self.__inner.append(item)

    def to_list(self):
        ret = self.__inner.copy()
        return ret

    def select(self, selector: Callable[[any], any]) -> 'EList':
        ret = EList()
        for it in self.__inner:
            new_it = selector(it)
            ret.append(new_it)
        return ret

    def where(self, predicate: Callable[[any], bool]) -> 'EList':
        ret = EList()
        for it in self.__inner:
            if predicate(it):
                ret.append(it)
        return ret

    def first_or_none(self, predicate: Callable[[any], bool] = None) -> Optional[any]:
        ret = None
        if predicate is not None:
            for it in self.__inner:
                if predicate(it):
                    ret = it
                    break
        else:
            if len(self.__inner) > 0:
                ret = self.__inner[0]
        return ret

    @staticmethod
    def of(items: List) -> 'EList':
        ret = EList(items)
        return ret
