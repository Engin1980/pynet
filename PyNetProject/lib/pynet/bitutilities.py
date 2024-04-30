from lib.esystem.easserting import EAssert
import numpy as np
import struct
from typing import List


class BitUtilities:
    class Int3D:
        @staticmethod
        def bytes_to_value(value: bytes) -> np.ndarray:
            INT_LEN = BitUtilities.Int.length()

            tmp = value[0:INT_LEN]  # TODO extract to separate function (repeated below)
            dim_a = BitUtilities.Int.bytes_to_value(tmp)
            tmp = value[INT_LEN: INT_LEN * 2]
            dim_b = BitUtilities.Int.bytes_to_value(tmp)
            tmp = value[INT_LEN * 2: INT_LEN * 3]
            dim_c = BitUtilities.Int.bytes_to_value(tmp)

            ret = np.zeros((dim_a, dim_b, dim_c), dtype=int)
            for i in range(dim_a):
                for j in range(dim_b):
                    si = INT_LEN * 3 + ((i * dim_b) + j) * dim_c * INT_LEN
                    tmp = value[si: si + dim_c * INT_LEN]
                    vals = BitUtilities.Int1D.bytes_to_value(tmp)
                    ret[i, j, :] = vals

            return ret

        @staticmethod
        def value_to_bytes(value: np.ndarray) -> bytes:
            EAssert.Argument.is_not_none(value)
            EAssert.Argument.is_true(len(value.shape) == 3)
            EAssert.Argument.is_true(value.dtype == int)

            dim_a_bytes: bytes = BitUtilities.Int.value_to_bytes(value.shape[0])
            dim_b_bytes: bytes = BitUtilities.Int.value_to_bytes(value.shape[1])
            dim_c_bytes: bytes = BitUtilities.Int.value_to_bytes(value.shape[2])

            pts = []
            for i in range(value.shape[0]):
                for j in range(value.shape[1]):
                    tmp = list(value[i, j, :])
                    pts.append(BitUtilities.Int1D.value_to_bytes(tmp))

            ret: bytearray = bytearray(dim_a_bytes) + bytearray(dim_b_bytes) + bytearray(dim_c_bytes)
            for it in pts:
                ret += it

            return ret

    class Int2D:
        @staticmethod
        def bytes_to_value(value: bytes) -> np.ndarray:
            INT_LEN = BitUtilities.Int.length()

            tmp = value[0:INT_LEN]
            dim_a = BitUtilities.Int.bytes_to_value(tmp)
            tmp = value[INT_LEN: INT_LEN * 2]
            dim_b = BitUtilities.Int.bytes_to_value(tmp)

            ret = np.zeros((dim_a, dim_b), dtype=int)
            for i in range(dim_a):
                si = INT_LEN * 2 + i * dim_b * INT_LEN
                tmp = value[si: si + dim_b * INT_LEN]
                vals = BitUtilities.Int1D.bytes_to_value(tmp)
                ret[i, :] = vals

            return ret

        @staticmethod
        def value_to_bytes(value: np.ndarray) -> bytes:
            EAssert.Argument.is_not_none(value)
            EAssert.Argument.is_true(len(value.shape) == 2)
            EAssert.Argument.is_true(value.dtype == int)

            dim_a_bytes: bytes = BitUtilities.Int.value_to_bytes(value.shape[0])
            dim_b_bytes: bytes = BitUtilities.Int.value_to_bytes(value.shape[1])

            pts = []
            for i in range(value.shape[0]):
                tmp = list(value[i, :])
                pts.append(BitUtilities.Int1D.value_to_bytes(tmp))

            ret: bytearray = bytearray(dim_a_bytes) + bytearray(dim_b_bytes)
            for it in pts:
                ret += it

            return ret

    class Float3D:

        @staticmethod
        def bytes_to_value(value: bytes) -> np.ndarray:
            INT_LEN = BitUtilities.Int.length()
            DBL_LEN = BitUtilities.Float.length()

            tmp = value[0:INT_LEN]
            dim_a = BitUtilities.Int.bytes_to_value(tmp)
            tmp = value[INT_LEN: INT_LEN * 2]
            dim_b = BitUtilities.Int.bytes_to_value(tmp)
            tmp = value[INT_LEN * 2: INT_LEN * 3]
            dim_c = BitUtilities.Int.bytes_to_value(tmp)

            ret = np.zeros((dim_a, dim_b, dim_c))
            for i in range(dim_a):
                for j in range(dim_b):
                    si = INT_LEN * 3 + ((i * dim_b) + j) * dim_c * DBL_LEN
                    tmp = value[si: si + dim_c * DBL_LEN]
                    vals = BitUtilities.Float1D.bytes_to_value(tmp)
                    ret[i, j, :] = vals

            return ret

        @staticmethod
        def value_to_bytes(value: np.ndarray) -> bytes:
            EAssert.Argument.is_not_none(value)
            EAssert.Argument.is_true(len(value.shape) == 3)

            dim_a_bytes: bytes = BitUtilities.Int.value_to_bytes(value.shape[0])
            dim_b_bytes: bytes = BitUtilities.Int.value_to_bytes(value.shape[1])
            dim_c_bytes: bytes = BitUtilities.Int.value_to_bytes(value.shape[2])

            pts = []
            for i in range(value.shape[0]):
                for j in range(value.shape[1]):
                    tmp = list(value[i, j, :])
                    pts.append(BitUtilities.Float1D.value_to_bytes(tmp))

            ret: bytearray = bytearray(dim_a_bytes) + bytearray(dim_b_bytes) + bytearray(dim_c_bytes)
            for it in pts:
                ret += it

            return ret

    class Float2D:
        @staticmethod
        def bytes_to_value(value: bytes) -> np.ndarray:
            INT_LEN = BitUtilities.Int.length()
            DBL_LEN = BitUtilities.Float.length()

            tmp = value[0:INT_LEN]
            dim_a = BitUtilities.Int.bytes_to_value(tmp)
            tmp = value[INT_LEN: INT_LEN * 2]
            dim_b = BitUtilities.Int.bytes_to_value(tmp)

            ret = np.zeros((dim_a, dim_b))
            for i in range(dim_a):
                si = INT_LEN * 2 + i * dim_b * DBL_LEN
                tmp = value[si: si + dim_b * DBL_LEN]
                vals = BitUtilities.Float1D.bytes_to_value(tmp)
                ret[i, :] = vals

            return ret

        @staticmethod
        def value_to_bytes(value: np.ndarray) -> bytes:
            EAssert.Argument.is_not_none(value)
            EAssert.Argument.is_true(len(value.shape) == 2)

            dim_a_bytes: bytes = BitUtilities.Int.value_to_bytes(value.shape[0])
            dim_b_bytes: bytes = BitUtilities.Int.value_to_bytes(value.shape[1])

            pts = []
            for i in range(value.shape[0]):
                tmp = list(value[i, :])
                pts.append(BitUtilities.Float1D.value_to_bytes(tmp))

            ret: bytearray = bytearray(dim_a_bytes) + bytearray(dim_b_bytes)
            for it in pts:
                ret += it

            return ret

    class Float1D:

        @staticmethod
        def bytes_to_value(value: bytes) -> List[float]:
            ret = []
            index = 0
            while index < len(value):
                part = value[index:index + BitUtilities.Float.length()]
                tmp = BitUtilities.Float.bytes_to_value(part)
                ret.append(tmp)
                index += BitUtilities.Float.length()
            return ret

        @staticmethod
        def value_to_bytes(value: List[float]) -> bytes:
            import struct
            ret = struct.pack("%sd" % len(value), *value)
            return ret

    class Int1D:

        @staticmethod
        def value_to_bytes(value: List[int]) -> bytes:
            import struct
            ret = struct.pack("%si" % len(value), *value)
            return ret

        @staticmethod
        def bytes_to_value(value: bytes) -> List[int]:
            ret = []
            index = 0
            while index < len(value):
                part = value[index:index + BitUtilities.Int.length()]
                tmp = BitUtilities.Int.bytes_to_value(part)
                ret.append(tmp)
                index += BitUtilities.Int.length()
            return ret

    class Str:

        @staticmethod
        def value_to_bytes(value: str) -> bytes:
            ret = value.encode("UTF-8")
            return ret

        @staticmethod
        def bytes_to_value(value: bytes) -> str:
            ret = value.decode("UTF-8")
            return ret

    class Float:

        @staticmethod
        def value_to_bytes(value: float) -> bytes:
            ret = struct.pack('<d', value)
            return ret

        @staticmethod
        def bytes_to_value(value: bytes) -> float:
            ret = struct.unpack('<d', value)
            ret = ret[0]
            return ret

        @staticmethod
        def length():
            return 8

    class Int:

        @staticmethod
        def value_to_bytes(value: int, byteorder='little') -> bytes:
            ret = value.to_bytes(4, byteorder, signed=True)
            return ret

        @staticmethod
        def bytes_to_value(value: bytes, byteorder='little', signed=True):
            ret = int.from_bytes(value, byteorder=byteorder, signed=signed)
            return ret

        @staticmethod
        def length():
            return 4

    class Bool:

        @staticmethod
        def bytes_to_value(value: bytes):
            ret = False if value[0] == 0 else True
            return ret

        @staticmethod
        def value_to_bytes(value: bool) -> bytes:
            ret = bytes([1]) if value else bytes([0])
            return ret

        @staticmethod
        def length():
            return 1

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
