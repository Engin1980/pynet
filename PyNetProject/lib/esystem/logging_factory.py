import logging
import sys
import typing
from lib.esystem.elist import EList
from lib.esystem.easserting import EAssert
import re


class _Filter(logging.Filter):
    def __init__(self, log_rules: typing.List['_LogRule']):
        super().__init__()
        EAssert.Argument.is_not_none(log_rules)
        EAssert.Argument.is_true(len(log_rules) > 0, "There are no rules specified for the filter.")
        self.__rules = log_rules

    def filter(self, record: logging.LogRecord) -> bool:
        rule = EList.of(self.__rules).first_or_none(lambda q: bool(re.search(q.pattern, record.name)))
        if rule is None:
            ret = False
        else:
            ret = rule.level <= record.levelno
        return ret


class _LogRule:
    def __init__(self, pattern: str, level: typing.Union[int, str]):
        self.pattern = pattern
        if isinstance(level, int):
            self.level = level
        else:
            self.level = _convert_log_string_to_int(level)

    @staticmethod
    def create_from_config(config: typing.Dict) -> '_LogRule':
        EAssert.is_true(_LOG_RULE_PATTERN_KEY in config.keys(),
                        f"Missing key {_LOG_RULE_PATTERN_KEY} in config for log-rule.")
        EAssert.is_true(_LOG_RULE_LEVEL_KEY in config.keys(),
                        f"Missing key {_LOG_RULE_LEVEL_KEY} in config for log-rule.")
        pattern = config[_LOG_RULE_PATTERN_KEY]
        level = config[_LOG_RULE_LEVEL_KEY]
        ret = _LogRule(pattern, level)
        return ret



_FORMAT_KEY = "format"
_HANDLERS_KEY = "handlers"
_CONSOLE_HANDLER_KEY = "console"
_FILE_HANDLER_KEY = "file"
_LOG_RULES_KEY = "rules"
_LOG_RULE_PATTERN_KEY = "pattern"
_LOG_RULE_LEVEL_KEY = "level"
#_formatter = logging.Formatter("{message}", style="$")
_formatter = logging.Formatter("%(message)s")
_filter: '_Filter' = _Filter([_LogRule(".+", logging.INFO)])
_handlers = []


def _convert_log_string_to_int(level) -> int:
    ret = logging.getLevelName(level)
    EAssert.is_true(isinstance(ret, int), f"Unable to convert {level} to predefined log-level int.")
    return ret


def init_by_config(config: typing.Dict) -> None:
    EAssert.is_not_none(config)
    global _formatter
    if _FORMAT_KEY in config.keys():
        format = config[_FORMAT_KEY]
        EAssert.is_true(isinstance(format, str))
        _formatter = logging.Formatter(fmt=format, style="{")

    if _LOG_RULES_KEY in config.keys():
        log_rules = []
        for lr_config in config[_LOG_RULES_KEY]:
            log_rule = _LogRule.create_from_config(lr_config)
            log_rules.append(log_rule)
        global _filter
        _filter = _Filter(log_rules)

    if _HANDLERS_KEY in config.keys():
        handlers = []
        for handler_key in config[_HANDLERS_KEY].keys():
            if handler_key == _CONSOLE_HANDLER_KEY and config[_HANDLERS_KEY][handler_key] == True:
                handler = logging.StreamHandler(sys.stdout)
                handler.setFormatter(_formatter)
                handlers.append(handler)
            if handler_key == _FILE_HANDLER_KEY:
                file_name = config[_HANDLERS_KEY][handler_key]
                if file_name is not None and len(file_name) > 0:
                    handler = logging.FileHandler(file_name)
                    handler.setFormatter(_formatter)
                    handlers.append(handler)
        global _handlers
        _handlers = handlers


def create_logger(name: str) -> logging.Logger:
    EAssert.is_not_none(name)

    ret = logging.Logger(name)
    global _filter
    ret.addFilter(_filter)

    global _handlers
    EList.of(_handlers).for_each(lambda q: ret.addHandler(q))

    return ret
