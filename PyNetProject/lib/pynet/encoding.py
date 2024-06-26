import re
from typing import Tuple
from lib.pynet.bitutilities import BitUtilities
from lib.esystem.elist import EList
from lib.pynet.exceptions import PyNetException
import numpy as np
from lib.esystem.easserting import EAssert


class _PyNetEncoder:
    def __init__(self, accepts_value, accepts_type_id,
                 to_type_id, to_data,
                 to_byte_len, to_value):
        self.accepts_value = accepts_value
        self.accepts_type_id = accepts_type_id
        self.to_type_id = to_type_id
        self.to_data = to_data
        self.to_byte_len = to_byte_len
        self.to_value = to_value


class PyNetEncoderManager:
    ENCODERS = EList.of([
        _PyNetEncoder(
            lambda q: q is None,
            lambda q: q == "n",
            lambda q: "n",
            lambda q: bytes(),
            lambda q: 0,
            lambda q: None
        ),
        _PyNetEncoder(
            lambda q: isinstance(q, str),
            lambda q: re.search("^s\\d+", q),
            lambda q: "s" + str(len(q)),
            lambda q: BitUtilities.Str.value_to_bytes(q),
            lambda q: int(q[1:]),
            lambda q: BitUtilities.Str.bytes_to_value(q)
        ),
        _PyNetEncoder(
            lambda q: isinstance(q, bool),
            lambda q: q == "b",
            lambda q: "b",
            lambda q: BitUtilities.Bool.value_to_bytes(q),
            lambda q: BitUtilities.Bool.length(),
            lambda q: BitUtilities.Bool.bytes_to_value(q)
        ),
        _PyNetEncoder(
            lambda q: isinstance(q, int),
            lambda q: q == "i",
            lambda q: "i",
            lambda q: BitUtilities.Int.value_to_bytes(q),
            lambda q: BitUtilities.Int.length(),
            lambda q: BitUtilities.Int.bytes_to_value(q)
        ),
        _PyNetEncoder(
            lambda q: isinstance(q, float),
            lambda q: q == "d",
            lambda q: "d",
            lambda q: BitUtilities.Float.value_to_bytes(q),
            lambda q: BitUtilities.Float.length(),
            lambda q: BitUtilities.Float.bytes_to_value(q)
        ),
        _PyNetEncoder(
            lambda q: isinstance(q, bytes),
            lambda q: re.search(r"^b\d+", q),
            lambda q: "b" + str(len(q)),
            lambda q: q,
            lambda q: int(q[1:]),
            lambda q: q
        ),
        _PyNetEncoder(
            lambda q: isinstance(q, list) and all(isinstance(d, float) for d in q),
            lambda q: re.search(r"^d\d+", q),
            lambda q: "d" + str(len(q) * BitUtilities.Float.length()),
            lambda q: BitUtilities.Float1D.value_to_bytes(q),
            lambda q: int(q[1:]),
            lambda q: BitUtilities.Float1D.bytes_to_value(q)
        ),
        _PyNetEncoder(
            lambda q: isinstance(q, np.ndarray) and len(q.shape) == 2 and q.dtype == float,
            lambda q: re.search(r"^md\d+", q),
            lambda q: "md" + str(
                np.array(q.shape).prod() * BitUtilities.Float.length()
                + 2 * BitUtilities.Int.length()),
            lambda q: BitUtilities.Float2D.value_to_bytes(q),
            lambda q: int(q[2:]),
            lambda q: BitUtilities.Float2D.bytes_to_value(q)
        ),
        _PyNetEncoder(
            lambda q: isinstance(q, np.ndarray) and len(q.shape) == 3 and q.dtype == float,
            lambda q: re.search(r"^mmd\d+", q),
            lambda q: "mmd" + str(
                np.array(q.shape).prod() * BitUtilities.Float.length()
                + 3 * BitUtilities.Int.length()),
            lambda q: BitUtilities.Float3D.value_to_bytes(q),
            lambda q: int(q[3:]),
            lambda q: BitUtilities.Float3D.bytes_to_value(q)
        ),
        _PyNetEncoder(
            lambda q: isinstance(q, list) and all(isinstance(d, int) for d in q),
            lambda q: re.search(r"^i\d+", q),
            lambda q: "i" + str(len(q) * BitUtilities.Int.length()),
            lambda q: BitUtilities.Int1D.value_to_bytes(q),
            lambda q: int(q[1:]),
            lambda q: BitUtilities.Int1D.bytes_to_value(q)
        ),
        _PyNetEncoder(
            lambda q: isinstance(q, np.ndarray) and len(q.shape) == 2 and q.dtype == int,
            lambda q: re.search(r"^mi\d+", q),
            lambda q: "mi" + str(
                np.array(q.shape).prod() * BitUtilities.Int.length()
                + 2 * BitUtilities.Int.length()),
            lambda q: BitUtilities.Int2D.value_to_bytes(q),
            lambda q: int(q[2:]),
            lambda q: BitUtilities.Int2D.bytes_to_value(q)
        ),
        _PyNetEncoder(
            lambda q: isinstance(q, np.ndarray) and len(q.shape) == 3 and q.dtype == int,
            lambda q: re.search(r"^mmi\d+", q),
            lambda q: "mmi" + str(
                np.array(q.shape).prod() * BitUtilities.Int.length()
                + 3 * BitUtilities.Int.length()),
            lambda q: BitUtilities.Int3D.value_to_bytes(q),
            lambda q: int(q[3:]),
            lambda q: BitUtilities.Int3D.bytes_to_value(q)
        )
    ])

    @staticmethod
    def encode(value) -> Tuple[str, bytes]:
        encoder = PyNetEncoderManager.__get_encoder_by_value(value)
        (type_id, data) = PyNetEncoderManager.__encode_with_encoder(encoder, value)
        return type_id, data

    @staticmethod
    def __get_encoder_by_value(value: any) -> _PyNetEncoder:
        ret = PyNetEncoderManager.ENCODERS.first_or_none(lambda q: q.accepts_value(value))
        if ret is None:
            raise PyNetException("Failed to find encoder for " + str(value))
        return ret

    @staticmethod
    def __encode_with_encoder(encoder: _PyNetEncoder, value: any) -> Tuple[str, bytes]:
        type_id = encoder.to_type_id(value)
        data = encoder.to_data(value)
        return type_id, data

    @staticmethod
    def decode(type_id: str, data_bytes: bytes) -> Tuple[any, int]:
        encoder = PyNetEncoderManager.__get_encoder_by_type_id(type_id)
        value, used_bytes = PyNetEncoderManager.__decode_with_encoder(encoder, type_id, data_bytes)
        return value, used_bytes

    @staticmethod
    def __get_encoder_by_type_id(type_id: str) -> _PyNetEncoder:
        ret = PyNetEncoderManager.ENCODERS.first_or_none(lambda q: q.accepts_type_id(type_id))
        if ret is None:
            raise PyNetException("Failed to find encoder for type-id " + str(type_id))
        return ret

    @staticmethod
    def __decode_with_encoder(encoder: _PyNetEncoder, type_id: str, data_bytes: bytes) -> Tuple[any, int]:
        EAssert.is_true(encoder.accepts_type_id(type_id))
        data_len = encoder.to_byte_len(type_id)
        data = data_bytes[:data_len]
        value = encoder.to_value(data)
        return value, data_len
