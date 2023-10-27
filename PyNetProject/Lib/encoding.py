import re
from typing import Tuple, List, Dict, Optional
from Lib.types import BitUtilities, EList
from Lib.types import PyNetException


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
            lambda q: re.search("s\\d+", q),
            lambda q: "s" + str(len(q)),
            lambda q: BitUtilities.str_to_bytes(q),
            lambda q: int(q[1:]),
            lambda q: BitUtilities.bytes_to_str(q)
        ),
        _PyNetEncoder(
            lambda q: isinstance(q, int),
            lambda q: q == "i",
            lambda q: "i",
            lambda q: BitUtilities.int_to_bytes(q),
            lambda q: BitUtilities.int_length(),
            lambda q: BitUtilities.bytes_to_int(q)
        ),
        _PyNetEncoder(
            lambda q: isinstance(q, float),
            lambda q: q == "f",
            lambda q: "f",
            lambda q: BitUtilities.float_to_bytes(q),
            lambda q: BitUtilities.float_length(),
            lambda q: BitUtilities.bytes_to_float(q)
        ),
        _PyNetEncoder(
            lambda q: isinstance(q, bool),
            lambda q: q == "b",
            lambda q: "b",
            lambda q: BitUtilities.bool_to_bytes(q),
            lambda q: BitUtilities.bool_length(),
            lambda q: BitUtilities.bytes_to_bool(q)
        ),
        _PyNetEncoder(
            lambda q: isinstance(q, bytes),
            lambda q: re.search("b\\d+", q),
            lambda q: "b" + str(len(q)),
            lambda q: q,
            lambda q: int(q[1:]),
            lambda q: q
        ),
    ])

    @staticmethod
    def encode(value) -> Tuple[str, bytes]:
        encoder = PyNetEncoderManager.__get_encoder_by_value(value)
        (type_id, data) = PyNetEncoderManager.__encode_with_encoder(encoder, value)
        return type_id, data

    @staticmethod
    def __get_encoder_by_value(value):
        ret = PyNetEncoderManager.ENCODERS.first_or_none(lambda q: q.accepts_value(value))
        if ret is None:
            raise PyNetException("Failed to find encoder for " + str(value))
        return ret

    @staticmethod
    def __encode_with_encoder(encoder: _PyNetEncoder, value: any) -> Tuple[str, bytes]:
        type_id = encoder.to_type_id(value)
        data = encoder.to_data(value)
        return type_id, data
