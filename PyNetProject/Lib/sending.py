from Lib.elogging import LogLevel
from Lib.easserting import EAssert
import socket
from Lib.types import PyNetException, AppException, BitUtilities, EList
from Lib.typing import Optional, Dict, List
from Lib.encoding import PyNetEncoderManager


class Sender:
    RESPONSE_SIZE = 4
    next_request_id = 1

    def _log(self, level: LogLevel, msg: str) -> None:
        # TODO resolve
        print(f"LOG {level} : {msg}")
        # if self._logger is not None:
        #     self._logger.log(level, msg, sender=f"Sender {self.__host}:{self.__port}")

    def __init__(self, host: str, port: int):
        EAssert.Argument.is_nonempty_string(host)
        EAssert.Argument.is_true(port > 0)

        self.__host = host
        self.__port = port

        self._log(LogLevel.MAIN, f"Sender over {host}:{port} created.")

    def send_object(self, obj: any) -> int:
        #TODO kontrola na typ, že je třída
        EAssert.Argument.is_true(hasattr(obj, "__dict__"), "Object with __dict_ expected")
        dictionary = vars(obj)
        return self.send_dict(dictionary)

    def send_dict(self, dictionary: Dict) -> int:
        EAssert.Argument.is_not_none(dictionary)

        dictionary["rid"] = Sender.next_request_id
        Sender.next_request_id += 1

        try:
            (header, data) = self.__encode_message(dictionary)
        except Exception as e:
            raise PyNetException("Failed to serialize message.", e)

        self.__send_via_port(header, data)

        return dictionary["rid"]

    def __encode_message(self, dictionary: Dict) -> (str, bytes):

        def join_byte_arrays(array: List[bytes]) -> bytes:
            return b''.join(array)

        h = EList()
        d = EList()

        for key in dictionary.keys():
            val = dictionary[key]
            (val_type, val_data) = PyNetEncoderManager.encode(val)
            h.append(_KeyValue(key,val_type))
            d.append(val_data)

        header = ";".join(h.select(lambda q: f"{q.key}:{q.value}").to_list())
        data = join_byte_arrays(d.to_list())

        return header, data

    def __send_via_port(self, header: str, data_bytes: bytearray):
        socket = _ESocket(self.__host, self.__port)

        header_bytes = BitUtilities.str_to_bytes(header)
        header_len = BitUtilities.int_to_bytes(len(header_bytes))
        data_len = BitUtilities.int_to_bytes(len(data_bytes))

        socket.open()
        socket.send(header_len)
        socket.send(data_len)
        socket.send(header_bytes)
        socket.send(data_bytes)
        socket.close()


class _ESocket:
    def __init__(self, host: str, port: int):
        EAssert.Argument.is_nonempty_string(host)
        EAssert.Argument.is_true(port > 0)

        self.__host = host
        self.__port = port
        self.__socket = None

    def open(self):
        EAssert.is_none(self.__socket)

        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.__socket.connect((self.__host, self.__port))
        except Exception as e:
            self.__socket = None
            raise PyNetException("Unable to open connection.", e)

    def send(self, byte_data: bytes) -> None:
        if len(byte_data) == 0:
            return
        EAssert.is_true(self.is_opened)

        self.__socket.sendall(byte_data)

        # try:
        #     result = self.__socket.recv(Sender.RESPONSE_SIZE)
        # except Exception as e:
        #     raise PyNetException("Send-confirmation not received.", e)

    @property
    def is_opened(self) -> bool:
        return self.__socket is not None

    def close(self):
        if self.__socket is not None:
            self.__socket.close()
            self.__socket = None


class _KeyValue:
    def __init__(self, key, value):
        EAssert.Argument.is_not_none(key)
        self.__key = key
        self.__value = value

    @property
    def key(self):
        return self.__key

    @property
    def value(self):
        return self.__value

    def __str__(self):
        return f"{self.key}={self.value}"
