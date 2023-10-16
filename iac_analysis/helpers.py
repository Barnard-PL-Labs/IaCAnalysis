from typing import Any, Callable, TypeVar


T = TypeVar("T")


def find_first(l: list[T], predicate: Callable[[T], bool]):
    return next((item for item in l if predicate(item)), None)
