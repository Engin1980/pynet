# import datetime
# import sys
# from enum import IntEnum
# from Lib.easserting import EAssert
# from typing import Dict, List, Optional
# from threading import RLock
#
#
# class LogLevel(IntEnum):
#     DEBUG = 0,
#     CRITICAL = 1,
#     ERROR = 2,
#     WARNING = 3,
#     INFO = 4,
#     VERBOSE = 5
#
#     @staticmethod
#     def from_string(txt: str) -> 'LogLevel':
#         txt = txt.strip().lower()
#         if txt == "critical":
#             ret = LogLevel.CRITICAL
#         elif txt == "error":
#             ret = LogLevel.ERROR
#         elif txt == "warning":
#             ret = LogLevel.WARNING
#         elif txt == "info":
#             ret = LogLevel.INFO
#         elif txt == "verbose":
#             ret = LogLevel.VERBOSE
#         elif txt == "debug":
#             ret = LogLevel.DEBUG
#         else:
#             raise Exception(f"Unknown log-level string '{txt}'")
#         return ret
#
#
# class _LoggerCallbacks:
#     __thread_safe_print_lock = RLock()
#
#     def __init__(self):
#         self.__callbacks = []
#
#     def add_callback(self, name: str, callback) -> None:
#         callback = LoggerCallback(name, callback)
#         self.__callbacks.append(callback)
#
#     def add_log_to_file_callback(self, file_name: str) -> None:
#         def tmp(text: str):
#             with open(file_name, "a") as f:
#                 f.write(text)
#                 f.write('\n')
#
#         self.add_callback(f"FileLog '{file_name}' (generated)", tmp)
#
#     def add_log_console_callback(self) -> None:
#         def tmp(text: str):
#             with _LoggerCallbacks.__thread_safe_print_lock:
#                 print(text)
#                 sys.stdout.flush()
#
#         self.add_callback("ConsoleLog (generated)", tmp)
#
#     def invoke_all(self, text: str):
#         for callback in self.__callbacks:
#             try:
#                 callback.callback(text)
#             except Exception as e:
#                 raise LoggerException(f"Callback '{callback.name}' failed to invoke.", e)
#
#
# class _LoggerRules:
#     def __init__(self):
#         self.__rules = []
#
#     def add(self, rule: 'LoggerRule', add_as_first: bool = False) -> None:
#         EAssert.Argument.is_not_none(rule, "rule")
#         if add_as_first and len(self.__rules) > 0:
#             self.__rules.insert(0, rule)
#         else:
#             self.__rules.append(rule)
#
#     def clear(self):
#         self.__rules.clear()
#
#     def add_list(self, rules: List['LoggerRule']) -> None:
#         EAssert.Argument.is_not_none(rules, "rules")
#         for rule in rules:
#             self.add(rule)
#
#     def try_get_first_applicable(self, logger_name: str) -> Optional['LoggerRule']:
#         ret = None
#         for lr in self.__rules:
#             if lr.is_match(logger_name):
#                 ret = lr
#                 break
#         return ret
#
#
# class Logger:
#     __callbacks = _LoggerCallbacks()
#     __rules = _LoggerRules()
#
#     @staticmethod
#     def get_callbacks() -> _LoggerCallbacks:
#         return Logger.__callbacks
#
#     @staticmethod
#     def get_rules() -> _LoggerRules:
#         return Logger.__rules
#
#     def __init__(self, sender: str):
#         self.__sender = sender
#
#     def log(self, log_level: LogLevel, message: str, sender: str = None):
#         log(log_level, message, self.__sender if sender is None else self.__sender + " (" + sender + ")")
#
#     def log_exception(self, log_level: LogLevel, exception: Exception, sender: str = None) -> None:
#         log_exception(log_level, exception, self.__sender if sender is None else self.__sender + " (" + sender + ")")
#
#
# class LoggerException(Exception):
#     def __init__(self, message, cause=None):
#         super().__init__(message, cause)
#
#
# class LoggerCallback:
#     def __init__(self, name: str, callback):
#         self.__name = name
#         self.__callback = callback
#
#     @property
#     def name(self):
#         return self.__name
#
#     @property
#     def callback(self):
#         return self.__callback
#
#
# class LoggerRule:
#
#     def __init__(self, source_regex: str, minimal_log_level: LogLevel):
#         EAssert.Argument.is_nonempty_string(source_regex,
#                                             f'"source_regex" cannot be empty or null, provided: {source_regex}')
#         EAssert.Argument.is_not_none(minimal_log_level,
#                                      f'"minimal_log_level" must contain minimal log level and cannot be debug')
#         EAssert.Argument.is_true(isinstance(minimal_log_level, LogLevel),
#                                  "'minimal_log_leve' is supposed to be of type LogLevel")
#         self.__regex = source_regex
#         self.__log_level = minimal_log_level
#
#     def log_level(self) -> LogLevel:
#         return self.__log_level
#
#     def is_match(self, log_name: str) -> bool:
#         import re
#         m = re.match(self.__regex, log_name)
#         return m is not None
#
#     def accepts_log_level(self, log_level: LogLevel) -> bool:
#         ret = log_level <= self.__log_level
#         return ret
#
#
# # region Global methods
#
# def log(level: LogLevel, text: str, sender: str = "") -> None:
#     EAssert.Argument.is_not_none(sender, "sender")
#     log_rule = Logger.get_rules().try_get_first_applicable(sender)
#     if log_rule is None:
#         msg = __format_log_message(LogLevel.WARNING, f"No log rule found for sender '{sender}'.")
#         __log_final(msg)
#     elif not log_rule.accepts_log_level(level):
#         return
#
#     msg = __format_log_message(level, text, sender)
#     __log_final(msg)
#
#
# def log_exception(log_level: LogLevel, exception: Exception, sender: str = "") -> None:
#     EAssert.Argument.is_not_none(exception, "exception")
#     EAssert.Argument.is_not_none(sender, "sender")
#     msg = str(exception)
#     import traceback
#     stack_trace_string = "".join(traceback.TracebackException.from_exception(exception).format())
#     log(log_level, msg + " stack-trace:: " + stack_trace_string, sender)
#
#     log(log_level, msg, sender)
#
#
# def __format_log_message(level: LogLevel, text: str, sender: str = "") -> str:
#     now = datetime.datetime.now()
#     who = sender
#     now_string = f"{now.year:04}-{now.month:02}-{now.day:02} {now.hour:02}:{now.minute:02}:{now.second:02}.{now.microsecond / 1000:03.0f}"
#     import threading
#     thread_id = threading.current_thread().name
#     msg = f"{now_string}; T:{thread_id:<15s}; {str(level)[9:]:<9s}; {who:<25s}; {text}"
#     return msg
#
#
# def __log_final(text: str) -> None:
#     Logger.get_callbacks().invoke_all(text)
