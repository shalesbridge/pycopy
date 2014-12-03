#!/usr/bin/env python

import os
import six
import collections

    

def _os_walk_pycopy(src, dst, xform_fn=lambda x, y: y):
    dirs = collections.deque()
    files = collections.deque()
    todo = collections.deque(os.listdir(src))
    while len(todo) > 0:
        x = todo.pop()
        if os.path.isdir(os.path.join(src, x)):
            d = os.path.join(x)
            if xform_fn
        else:
            todo.append(os.path.join(src, x))



pycopy = _os_walk_pycopy

def _scandir_pycopy(src, dst):
    pass

try:
    import scandir
    pycopy = _scandir_pycopy
except ImportError:
    pass
