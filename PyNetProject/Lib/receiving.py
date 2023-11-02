from Lib.easserting import EAssert
from Lib.elogging import LogLevel
from Lib.encoding import PyNetEncoderManager
from Lib.events import Event
from Lib.etypes import BitUtilities, AppException
from typing import Tuple, Optional
import threading
import socket


class Receiver:

    def __log(self, level: LogLevel, msg: str) -> None:
        self.__on_log.invoke(source=self, log_level=level, message=msg)

    def __init__(self, host: str, port: int, name: Optional[str] = None):
        EAssert.Argument.is_nonempty_string(host)
        EAssert.Argument.is_true(port > 0)

        self.__str_name = name if name is not None else f"Recv_{host}:{port}"
        self.__host = host
        self.__port = port
        self.__on_log = Event(source=any, log_level=LogLevel, message=str)
        self.__listener_thread = None

        self.__on_listening_started = Event(source=Receiver)
        self.__on_listening_stopped = Event(source=Receiver)
        self.__on_client_connected = Event(source=Receiver, client_id=int)
        self.__on_client_disconnected = Event(source=Receiver, client_id=int)
        self.__on_message_received = Event(source=Receiver, client_id=int, message=dict)

    @property
    def on_log(self) -> Event:
        return self.__on_log

    @property
    def host(self) -> str:
        return self.__host

    @property
    def port(self) -> int:
        return self.__port

    @property
    def on_listening_started(self) -> Event:
        return self.__on_listening_started

    @property
    def on_listening_stopped(self) -> Event:
        return self.__on_listening_stopped

    @property
    def on_client_connected(self) -> Event:
        return self.__on_client_connected

    @property
    def on_client_disconnected(self) -> Event:
        return self.__on_client_disconnected

    @property
    def on_message_received(self) -> Event:
        return self.__on_message_received

    def start(self):
        EAssert.Argument.is_false(self.is_running)
        self.__listener_thread = _ListenerThread(self)
        self.__log(LogLevel.VERBOSE, "Starting")
        self.__listener_thread.start()
        self.__log(LogLevel.INFO, f"Started")

    def stop_async(self):
        EAssert.Argument.is_true(self.is_running)
        self.__log(LogLevel.VERBOSE, "Stopping async requesting")
        self.__listener_thread.break_listening()
        self.__log(LogLevel.INFO, "Stopping async requested")

    @property
    def is_running(self):
        return self.__listener_thread is not None

    def __str__(self):
        return self.__str_name


class _ListenerThread(threading.Thread):
    BUFFER_SIZE = 1024
    STATE_RUNNING = 1
    STATE_STOPPING = 2
    STATE_OFF = 0
    NEXT_CLIENT_ID = 1

    def __log(self, log_level: LogLevel, message: str) -> None:
        self.__parent.on_log.invoke(source=str(self.__parent) + "/TL", log_level=log_level, message=message)

    def __init__(self, parent: Receiver):
        super().__init__()
        self.__parent = parent
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__log(LogLevel.VERBOSE, "Binding port")
        self.__socket.bind((self.__parent.host, self.__parent.port))
        self.__log(LogLevel.VERBOSE, "Bound")
        self.__state = _ListenerThread.STATE_OFF

    def run(self):
        self.__log(LogLevel.INFO, "Running")
        self.__state = _ListenerThread.STATE_RUNNING
        self.__log(LogLevel.VERBOSE, "Starting listening")
        self.__socket.listen()
        self.__log(LogLevel.VERBOSE, "Listening")
        self.__parent.on_listening_started.invoke(source=self.__parent)

        while self.__state == _ListenerThread.STATE_RUNNING:
            try:
                self.__log(LogLevel.VERBOSE, "Waiting for a client")
                conn, addr = self.__socket.accept()
            except OSError as e:
                self.__log(LogLevel.VERBOSE, f"Waiting for a client throws an error {e}")
                EAssert.is_true(e.errno == 10038,
                                f"Unexpected error {e.errno} when accepting on socket.")
                break

            client_id = _ListenerThread.NEXT_CLIENT_ID
            _ListenerThread.NEXT_CLIENT_ID += 1
            self.__log(LogLevel.VERBOSE, f"Got a client {client_id}")
            self.__parent.on_client_connected.invoke(source=self.__parent, client_id=client_id)

            thr = _ConnectionReaderThread(conn, addr, client_id, self.__parent)
            thr.start()
            self.__log(LogLevel.VERBOSE, f"Client {client_id} processing started")

        self.__socket = None
        self.__log(LogLevel.VERBOSE, "Stopping")
        self.__parent.on_listening_stopped.invoke(source=self.__parent)
        self.__log(LogLevel.INFO, "Stopped")

    def break_listening(self):
        self.__state = _ListenerThread.STATE_STOPPING
        self.__log(LogLevel.VERBOSE, "Closing socket")
        self.__socket.close()
        self.__log(LogLevel.VERBOSE, "Socket closed")

    # def __str__(self):
    #     return self.__str_id


class _ConnectionReaderThread(threading.Thread):

    def __log(self, level: LogLevel, msg: str) -> None:
        self.__parent.on_log.invoke(source=f"{self.__parent}/RD{self.__client_id}", log_level=level, message=msg)

    def __init__(self, conn, addr, client_id: int, parent: Receiver):
        super().__init__()
        self.__conn = conn
        self.__addr = addr
        self.__client_id = client_id
        self.__parent = parent
        self.__log(LogLevel.VERBOSE, "Created")

    def __read_intro_bytes(self) -> Tuple[int, int]:
        key_len_bytes = self.__conn.recv(4)
        if len(key_len_bytes) == 0:
            return 0, 0
        else:
            body_len_bytes = self.__conn.recv(4)

        EAssert.is_true(len(key_len_bytes) == 4)
        EAssert.is_true(len(body_len_bytes) == 4)
        key_len = BitUtilities.bytes_to_int(key_len_bytes)
        body_len = BitUtilities.bytes_to_int(body_len_bytes)

        return key_len, body_len

    def __read_out_byte_block(self, target_length: int) -> bytes:
        data = bytearray(target_length)
        remaining_bytes = target_length
        while remaining_bytes > 0:
            block_length = min(remaining_bytes, _ListenerThread.BUFFER_SIZE)
            block = self.__conn.recv(block_length)
            if len(block) < block_length:
                raise AppException("Connection contains no data. Mismatch?")
            start_index = target_length - remaining_bytes
            data[start_index:start_index + block_length] = block
            remaining_bytes -= block_length
        ret = bytes(data)
        return ret

    def run(self):
        self.__log(LogLevel.INFO, "Client connected - run")

        self.__log(LogLevel.VERBOSE, "Reading lengths")
        header_length, data_length = self.__read_intro_bytes()
        self.__log(LogLevel.VERBOSE, "Reading header")
        header_bytes = self.__read_out_byte_block(header_length)
        self.__log(LogLevel.VERBOSE, "Reading data")
        data_bytes = self.__read_out_byte_block(data_length)

        self.__log(LogLevel.VERBOSE, "Sending response")
        # send response:
        # resp = b'0000'
        # self.__conn.sendall(resp)

        self.__log(LogLevel.VERBOSE, "Decoding message")
        message = self.__expand_header_bytes_to_dictionary(header_bytes, data_bytes)

        self.__log(LogLevel.VERBOSE, "Invoking listener")
        self.__parent.on_message_received.invoke(source=self.__parent, client_id=self.__client_id, message=message)

        left_bytes = self.__conn.recv(_ListenerThread.BUFFER_SIZE)
        EAssert.is_true(0 == len(left_bytes), f"Unexpectingly, there are some data left in the incoming connection")

        self.__log(LogLevel.VERBOSE, "Invoking client disconnected")
        self.__parent.on_client_disconnected.invoke(source=self.__parent, client_id=self.__client_id)
        self.__log(LogLevel.INFO, "Client connected - run finished")

    def __expand_header_bytes_to_dictionary(self, header_bytes: bytes, data_bytes: bytes) -> dict:
        tmp = header_bytes.decode('UTF-8')
        pts = tmp.split(';')
        ret = {}

        data_start_index = 0
        for pt in pts:
            kv = pt.split(':')
            key = kv[0]
            value, used_bytes = PyNetEncoderManager.decode(kv[1], data_bytes[data_start_index:])
            data_start_index += used_bytes
            ret[key] = value

        return ret
