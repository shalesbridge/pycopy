#!/usr/bin/env python

import os
import shutil
import six
import collections

    

def _os_walk_pycopy(
    src, dst, 
    src_listdir_fn=os.listdir,
    copy_fn=shutil.copy,
    xform_fn=lambda src_base, src_dirname, src_basename: src_basename
):
    todo = collections.deque(('',))
        
    while len(todo) > 0:
        x = todo.pop()
        #if xform_fn(src, x['dirname'], x['basename']) == None:
        #    continue
        filespec = os.path.join(src, x['dirname'], x['basename'])
        if os.path.isdir(filespec):
            for y in src_listdir_fn(filespec):
                todo.append( 
                    { 
                        'dirname': os.path.join(x['dirname'], x['basename']),
                        'basename': y
                    }
        else:
            xformed_name = xform_fn(src, x['dirname'], x['basename']) 
            if xformed_name is None:
                #if os.path.exists(filespec):
                #    os.remove(filespec)
                continue
            copy_fn(
                os.path.join(filespec),
                xformed_name
            )



pycopy = _os_walk_pycopy

def _scandir_pycopy(src, dst):
    pass

try:
    import scandir
    pycopy = _scandir_pycopy
except ImportError:
    pass
