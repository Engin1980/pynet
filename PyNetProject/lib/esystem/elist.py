from typing import Callable, NoReturn, Optional, List
from lib.esystem.easserting import EAssert


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

    def for_each(self, action: Callable[[any], NoReturn]) -> None:
        EAssert.Argument.is_not_none(action)
        for it in self.__inner:
            action(it)
