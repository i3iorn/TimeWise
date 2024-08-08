import time
from typing import Callable

from src.utils.dll import Node, DoublyLinkedList


def cache(func: Callable, max_size: int = 128, timeout: int = 0) -> Callable:
    """
    A decorator that caches the results of a function call for a specified amount of time. The cache has a maximum size
    and will remove the oldest entry if the cache is full. The cache uses a combination of a dictionary and a
    doubly-linked list. The dictionary provides fast access to the cache entries, and the doubly-linked list provides
    fast removal of the oldest entry.

    Args:
        func (function): The function to cache.
        max_size (int): The maximum size of the cache.
        timeout (int): The time in seconds to keep the cache entries.

    Returns:
        function: The cached function.

    Example:
        @cache
        def foo(bar):
            return bar * bar
    """
    def wrapper(*args, **kwargs):
        if timeout > 0 and wrapper.cache_list.head:
            while time.time() - wrapper.cache_list.head.timestamp > timeout:
                del wrapper.cache[wrapper.cache_list.head.data]
                wrapper.cache_list.delete(wrapper.cache_list.head)
                if not wrapper.cache_list.head:
                    break

        key = (args, frozenset(kwargs.items()))
        if key in wrapper.cache:
            node = wrapper.cache[key]
            wrapper.cache_list.delete(node)
            wrapper.cache_list.append(node)
            return node.data
        result = func(*args, **kwargs)
        if len(wrapper.cache) >= max_size:
            del wrapper.cache[wrapper.cache_list.head.data]
            wrapper.cache_list.delete(wrapper.cache_list.head)
        node = Node(key)
        wrapper.cache[key] = node
        wrapper.cache_list.append(node)
        return result

    wrapper.cache = {}
    wrapper.cache_list = DoublyLinkedList()

    return wrapper
