#!/usr/bin/env python

"""
Copyright (c) 2006-2019 sqlmap developers (http://sqlmap.org/)
See the file 'LICENSE' for copying permission
"""

import functools
import hashlib
import threading

from lib.core.settings import MAX_CACHE_ITEMS
from lib.core.datatype import LRUDict
from lib.core.threads import getCurrentThreadData

_lock = threading.Lock()

def cachedmethod(f, cache=LRUDict(capacity=MAX_CACHE_ITEMS)):
    """
    Method with a cached content

    Reference: http://code.activestate.com/recipes/325205-cache-decorator-in-python-24/
    """

    @functools.wraps(f)
    def _(*args, **kwargs):
        with _lock:
            key = int(hashlib.md5("|".join(str(_) for _ in (f, args, kwargs))).hexdigest(), 16) & 0x7fffffffffffffff
            if key not in cache:
                cache[key] = f(*args, **kwargs)

            return cache[key]

    return _

def stackedmethod(f):
    """
    Method using pushValue/popValue functions (fallback function for stack realignment)
    """

    @functools.wraps(f)
    def _(*args, **kwargs):
        threadData = getCurrentThreadData()
        originalLevel = len(threadData.valueStack)

        try:
            result = f(*args, **kwargs)
        finally:
            if len(threadData.valueStack) > originalLevel:
                threadData.valueStack = threadData.valueStack[:originalLevel]

        return result

    return _
