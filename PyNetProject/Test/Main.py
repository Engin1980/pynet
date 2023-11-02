import time

from Lib.elogging import LogLevel
from Lib.receiving import Receiver
from Lib.sending import Sender
from threading import RLock

print_lock = RLock()

def process_log_message(source: any, log_level: LogLevel, message: str) -> None:
    print_lock.acquire()
    print(f"{str(source):20s}\t{log_level.name:10s}\t{message}")
    print_lock.release()


def receiver_message_handler(source: Receiver, client_id: int, message: dict):
    sender = Sender("localhost", 7007)
    sender.send_dict(message)


print("Starting listener")

receiver = Receiver("localhost", 8008)
receiver.on_message_received.add_listener(receiver_message_handler)
receiver.on_log.add_listener(process_log_message)
receiver.start()

time.sleep(600)
