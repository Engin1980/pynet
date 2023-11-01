from Lib.easserting import EAssert
from Lib.elogging import LogLevel
from Lib.encoding import PyNetEncoderManager
from Lib.events import Event
from typing import Tuple
import threading
import socket

from Lib.types import BitUtilities, AppException


class Receiver:
    def _log(self, level: LogLevel, msg: str) -> None:
        print(f"Receiver log: {level}: {msg}")

    def __init__(self, host: str, port: int):
        EAssert.Argument.is_nonempty_string(host)
        EAssert.Argument.is_true(port > 0)

        self._host = host
        self._port = port
        self._listener_thread = None

        self._on_listening_started = Event(source=Receiver)
        self._on_listening_stopped = Event(source=Receiver)
        self._on_client_connected = Event(source=Receiver, client_id=int)
        self._on_client_disconnected = Event(source=Receiver, client_id=int)
        self._on_message_received = Event(source=Receiver, client_id=int, message=dict)

        self._log(LogLevel.MAIN, f"Receiver over {host}:{port} created.")

    @property
    def on_listening_started(self) -> Event:
        return self._on_listening_started

    @property
    def on_listening_stopped(self) -> Event:
        return self._on_listening_stopped

    @property
    def on_client_connected(self) -> Event:
        return self._on_client_connected

    @property
    def on_client_disconnected(self) -> Event:
        return self._on_client_disconnected

    @property
    def on_message_received(self) -> Event:
        return self._on_message_received

    def start(self):
        EAssert.Argument.is_false(self.is_running)
        self._listener_thread = _ListenerThread(self)
        self._log(LogLevel.VERBOSE, "Starting")
        self._listener_thread.start()
        self._log(LogLevel.MAIN, f"Started")

    def stop_async(self):
        EAssert.Argument.is_true(self.is_running)
        self._log(LogLevel.VERBOSE, "Stopping async requesting")
        self._listener_thread.break_listening()
        self._log(LogLevel.INFO, "Stopping async requested")

    def __str__(self):
        return "Receiver_" + str(id(self))

    @property
    def is_running(self):
        return self._listener_thread is not None


class _ListenerThread(threading.Thread):
    BUFFER_SIZE = 1024
    STATE_RUNNING = 1
    STATE_STOPPING = 2
    STATE_OFF = 0
    NEXT_CLIENT_ID = 1

    def _log(self, level: LogLevel, msg: str) -> None:
        if self._parent._logger is not None:
            self._parent._logger.log(level, msg, sender=f"Lst")

    def __init__(self, parent: Receiver):
        super().__init__()
        self._parent = parent
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._log(LogLevel.VERBOSE, "Binding port")
        self._socket.bind((self._parent._host, self._parent._port))
        self._log(LogLevel.VERBOSE, "Bound")
        self._state = _ListenerThread.STATE_OFF

    def run(self):
        self._log(LogLevel.INFO, "Running")
        self._state = _ListenerThread.STATE_RUNNING
        self._log(LogLevel.VERBOSE, "Starting listening")
        self._socket.listen()
        self._log(LogLevel.VERBOSE, "Listening")
        self._parent.on_listening_started.invoke(source=self._parent)

        while self._state == _ListenerThread.STATE_RUNNING:
            try:
                self._log(LogLevel.VERBOSE, "Waiting for a client")
                conn, addr = self._socket.accept()
            except OSError as e:
                self._log(LogLevel.VERBOSE, f"Waiting for a client throws an error {e}")
                EAssert.is_true(e.errno == 10038,
                                f"Unexpected error {e.errno} when accepting on socket.")
                break

            client_id = _ListenerThread.NEXT_CLIENT_ID
            _ListenerThread.NEXT_CLIENT_ID += 1
            self._log(LogLevel.VERBOSE, f"Got a client {client_id}")
            self._parent.on_client_connected.invoke(source=self._parent, client_id=client_id)

            thr = _ConnectionReaderThread(conn, addr, client_id, self._parent)
            thr.start()
            self._log(LogLevel.VERBOSE, f"Client {client_id} processing started")

        self._socket = None
        self._log(LogLevel.VERBOSE, "Stopping")
        self._parent.on_listening_stopped.invoke(source=self._parent)
        self._log(LogLevel.INFO, "Stopped")

    def break_listening(self):
        self._state = _ListenerThread.STATE_STOPPING
        self._log(LogLevel.VERBOSE, "Closing socket")
        self._socket.close()
        self._log(LogLevel.VERBOSE, "Socket closed")


class _ConnectionReaderThread(threading.Thread):

    def __log(self, level: LogLevel, msg: str) -> None:
        print(f"CRT {level} \t {msg}")

    def __init__(self, conn, addr, client_id: int, parent: Receiver):
        super().__init__()
        self._conn = conn
        self._addr = addr
        self._client_id = client_id
        self._parent = parent

        self.__log(LogLevel.VERBOSE, "Created")

    def __read_intro_bytes(self) -> Tuple[int, int]:
        key_len_bytes = self._conn.recv(8)
        if len(key_len_bytes) == 0:
            return 0, 0
        else:
            body_len_bytes = self._conn.recv(8)

        key_len = BitUtilities.bytes_to_int(key_len_bytes)
        body_len = BitUtilities.bytes_to_int(body_len_bytes)

        return key_len, body_len

    def __read_out_byte_block(self, target_length: int) -> bytes:
        data = bytes(0)
        while len(data) < target_length:
            block = self._conn.recv(_ListenerThread.BUFFER_SIZE)
            if len(block) == 0:
                raise AppException("Connection contains no data. Mismatch?")
            data = data + block
        return data

    def run(self):
        self.__log(LogLevel.INFO, "Client connected - run")
        while True:
            self.__log(LogLevel.VERBOSE, "Reading lengths")
            header_length, data_length = self.__read_intro_bytes()
            if header_length == 0:
                break
            self.__log(LogLevel.VERBOSE, "Reading header")
            header_bytes = self.__read_out_byte_block(header_length)
            self.__log(LogLevel.VERBOSE, "Reading data")
            data_bytes = self.__read_out_byte_block(data_length)

            self.__log(LogLevel.VERBOSE, "Sending response")
            # send response:
            resp = b'0000'
            self._conn.sendall(resp)

            self.__log(LogLevel.VERBOSE, "Decoding message")
            message = self.__expand_header_bytes_to_dictionary(header_bytes, data_bytes)

            self.__log(LogLevel.VERBOSE, "Invoking listener")
            self._parent.on_message_received.invoke(source=self._parent, client_id=self._client_id, message=message)

        self.__log(LogLevel.VERBOSE, "Invoking client disconnected")
        self._parent.on_client_disconnected.invoke(source=self._parent, client_id=self._client_id)
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

        return ret
