from enum import Enum, IntEnum
from Lib.easserting import EAssert
from Lib.events import Event
from Lib.elogging import LogLevel
import struct
from typing import List, Optional, Callable
import numpy as np


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
    def bytes_to_matrix3d(value: bytes) -> np.ndarray:
        INT_LEN = BitUtilities.int_length()
        DBL_LEN = BitUtilities.float_length()

        tmp = value[0:INT_LEN]
        dim_a = BitUtilities.bytes_to_int(tmp)
        tmp = value[INT_LEN: INT_LEN * 2]
        dim_b = BitUtilities.bytes_to_int(tmp)
        tmp = value[INT_LEN * 2: INT_LEN * 3]
        dim_c = BitUtilities.bytes_to_int(tmp)

        ret = np.zeros((dim_a, dim_b, dim_c))
        for i in range(dim_a):
            for j in range(dim_b):
                si = INT_LEN * 3 + ((i * dim_b) + j) * dim_c * DBL_LEN
                tmp = value[si: si + dim_c * DBL_LEN]
                vals = BitUtilities.bytes_to_list(tmp)
                ret[i, j, :] = vals

        return ret

    @staticmethod
    def matrix3d_to_bytes(value: np.ndarray) -> bytes:
        EAssert.Argument.is_not_none(value)
        EAssert.Argument.is_true(len(value.shape) == 3)

        dim_a_bytes: bytes = BitUtilities.int_to_bytes(value.shape[0])
        dim_b_bytes: bytes = BitUtilities.int_to_bytes(value.shape[1])
        dim_c_bytes: bytes = BitUtilities.int_to_bytes(value.shape[2])

        pts = []
        for i in range(value.shape[0]):
            for j in range(value.shape[1]):
                tmp = list(value[i, j, :])
                pts.append(BitUtilities.list_to_bytes(tmp))

        ret: bytearray = bytearray(dim_a_bytes) + bytearray(dim_b_bytes) + bytearray(dim_c_bytes)
        for it in pts:
            ret += it

        return ret

    @staticmethod
    def bytes_to_matrix2d(value: bytes) -> np.ndarray:
        INT_LEN = BitUtilities.int_length()
        DBL_LEN = BitUtilities.float_length()

        tmp = value[0:INT_LEN]
        dim_a = BitUtilities.bytes_to_int(tmp)
        tmp = value[INT_LEN: INT_LEN * 2]
        dim_b = BitUtilities.bytes_to_int(tmp)

        ret = np.zeros((dim_a, dim_b))
        for i in range(dim_a):
            si = INT_LEN * 2 + i * dim_b * DBL_LEN
            tmp = value[si: si + dim_b * DBL_LEN]
            vals = BitUtilities.bytes_to_list(tmp)
            ret[i, :] = vals

        return ret

    @staticmethod
    def matrix2d_to_bytes(value: np.ndarray) -> bytes:
        EAssert.Argument.is_not_none(value)
        EAssert.Argument.is_true(len(value.shape) == 2)

        dim_a_bytes: bytes = BitUtilities.int_to_bytes(value.shape[0])
        dim_b_bytes: bytes = BitUtilities.int_to_bytes(value.shape[1])

        pts = []
        for i in range(value.shape[0]):
            tmp = list(value[i, :])
            pts.append(BitUtilities.list_to_bytes(tmp))

        ret: bytearray = bytearray(dim_a_bytes) + bytearray(dim_b_bytes)
        for it in pts:
            ret += it

        return ret

    @staticmethod
    def bytes_to_list(value: bytes) -> List[float]:
        ret = []
        index = 0
        while index < len(value):
            part = value[index:index + BitUtilities.float_length()]
            tmp = BitUtilities.bytes_to_float(part)
            ret.append(tmp)
            index += BitUtilities.float_length()
        return ret

    @staticmethod
    def list_length(value: List[float]) -> int:
        ret = len(value) * BitUtilities.float_length()
        return ret

    @staticmethod
    def list_to_bytes(value: List[float]) -> bytes:
        import struct
        ret = struct.pack("%sd" % len(value), *value)
        return ret

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
