#!/usr/bin/env python

import math
import os
import shutil
import six
import stat
import collections

"""
.. module:: pycopy
    :platform: Unix, Windows
    :synopsis: Recursively copy a directory.

.. moduleauthor:: Brandon Huber

"""

__version__ = '0.1'
    

try:
    import scandir
    _SCANDIR_FN = scandir
except ImportError:
    _SCANDIR_FN = fake_scandir.scandir

#try:
#    from math import isclose as _ISCLOSE_FN
#except ImportError:
#    raise NotImplementedError()

def default_xform_name(src_startdir, src_subdir, src_basename):
    ##########################################################################
    #
    # Because we have a valid path to the source file, we can check to see if
    # it's a directory or not should we need to.
    #
    # if os.path.is_dir(os.path.join(src_startdir, src_subdir, src_basename)):
    #   ...
    #
    ##########################################################################
    ##########################################################################
    #
    # If we decide we want to skip this file or directory, we just return None.
    #
    # return None
    #
    ##########################################################################
    ##########################################################################
    #
    # If we need to make any changes to what we want the name to be in the
    # destination directory, we can do so. E.g., we could replace all spaces
    # with underscores.
    #
    # return src_basename.replace(' ', '_')
    #
    ##########################################################################
    return src_basename

def should_copy(
    src_stat_result, dst_stat_result, use_size=True, use_mtime=True,
    mtime_tolerance=2.0
):
    """Tells whether a file should get overwritten.

    If the destination file *appears* to be the same as the source file,
    this function will indicate so by returning False.  Otherwise, it will
    return True.

    :param stat_result src_stat_result:
        The object returned by ``os.listdir`` for the source file.
    :param stat_result dst_stat_result:
        The object returned by ``os.listdir`` for the destination file.
    :param bool use_size:
        Whether or not to compare the sizes of the two files. (Default: True)
    :param bool use_mtime:
        Whether or not to compare the mtimes of the two files. (Default: True)
    :param float mtime_tolerance:
        By how many seconds the two files' mtimes are allowed to differ and
        still be considered equivalent. Note that FAT filesystems have a
        2-second resolution. (Default: 2.0)
    :returns:
        True if the two files appear to be dissimilar.  False otherwise.
    :rtype: bool

    """
    if use_size and src_stat_result.st_size != dst_stat_result.st_size:
        return True
    if (
        use_mtime
        and math.abs(stat_result.st_mtime - x.stat.st_mtime()) >
        mtime_tolerance
    ):
        return True
    return False

class DirEntry(object):
    def __init__(
        self,
        src_startdir, src_subdir, src_basename,
        dst_startdir, dst_subdir, dst_basename,
        _dbg_os_stat=os.stat
    ):
        self.src_startdir = src_startdir
        self.src_subdir = src_subdir
        self.src_basename = src_basename
        self.dst_startdir = dst_startdir
        self.dst_subdir = dst_subdir
        self.dst_basename = dst_basename
        self.stat = _dbg_os_stat(
            os.path.join(self.src_startdir, self.src_subdir, self.src_basename)
        )

    def is_dir(self):
        return stat.S_ISDIR(self.stat.st_mode)

    def is_file(self):
        return stat.S_ISREG(self.stat.st_mode)

    def size(self):
        return self.stat.st_size

def pycopy(
    src,
    dst, 
    copy_fn=shutil.copy,
    xform_fn=default_xform_name
):
    """Recursively copy a ``src`` directory to ``dst``.

    Recursively copies files and subdirectories from ``src`` to ``dst``,
    optionally excluding and/or changing the names of files and subdirectories
    based upon the function ``xform_fn``.

    ``xform_fn``, if given, should be a function that meets the following
    criteria:
        1. It takes three strings as parameters: ``src_base``, ``src_dirname``,
           and ``src_basename``.
        2. If the given source filespec is to be copied, a single string should
           be returned.  This string will be the desired basename of the
           destination file or directory.
        3. If the given source filespec should NOT be copied, then ``None``
           must be returned.  Note that if ``None`` is returned for a source
           filespec that represents a directory, pycopy will not recurse into
           that directory.

    """
    for dir_entry in cmp_dirs(src, dst, copy_fn=copy_fn, xform_fn=xform_fn):
        if dir_entry.is_dir():
            ###################################################################
            #
            # Create the destination directory if it does not already exist.
            #
            if not os.path.exists(
                os.path.join(
                    dir_entry.dst_startdir,
                    dir_entry.dst_subdir,
                    dir_entry.dst_basename,
                )
            ):
                os.makedirs(
                    os.path.join(
                        dir_entry.dst_startdir,
                        dir_entry.dst_subdir,
                        dir_entry.dst_basename
                    )
                )
            #
            ###################################################################
        else:
            dst_pathname = os.path.join(
                dir_entry.dst_startdir,
                dir_entry.dst_subdir,
                dir_entry.dst_basename
            )
            if (
                os.path.exists(dst_pathname)
                and not should_copy(dir_entry.stat, os.stat(dst_pathname))
            ):
                continue
            copy_fn(
                os.path.join(
                    dir_entry.src_startdir, dir_entry.src_subdir,
                    dir_entry.src_basename
                ),
                dst_pathname
            )



def cmp_dirs(
    src,
    dst, 
    copy_fn=shutil.copy,
    xform_fn=default_xform_name
):
    """Recursively compare a ``src`` directory to ``dst``.

    Recursively copies files and subdirectories from ``src`` to ``dst``,
    optionally excluding and/or changing the names of files and subdirectories
    based upon the function ``xform_fn``.

    ``xform_fn``, if given, should be a function that meets the following
    criteria:
        1. It takes three strings as parameters: ``src_base``, ``src_dirname``,
           and ``src_basename``.
        2. If the given source filespec is to be copied, a single string should
           be returned.  This string will be the desired basename of the
           destination file or directory.
        3. If the given source filespec should NOT be copied, then ``None``
           must be returned.  Note that if ``None`` is returned for a source
           filespec that represents a directory, pycopy will not recurse into
           that directory.

    """
    todo = collections.deque()
    todo.append(DirEntry(src, '', '', dst, '', ''))
        
    while len(todo) > 0:
        x = todo.pop()
        xformed_name = xform_fn(x.src_startdir, x.src_subdir, x.src_basename)
        if xformed_name is None:
            continue
        if x.is_dir():
            for y in os.listdir(
                os.path.join(x.src_startdir, x.src_subdir, x.src_basename)
            ):
                todo.append(
                    DirEntry(
                        x.src_startdir, 
                        os.path.join(x.src_subdir, x.src_basename),
                        y,
                        x.dst_startdir,
                        os.path.join(x.dst_subdir, x.dst_basename),
                        xformed_name
                    )
                )
        yield x

#def pycopy(
#    src,
#    dst, 
#    copy_fn=shutil.copy,
#    xform_fn=lambda src_base, src_dirname, src_basename: src_basename,
#):
#    """Recursively copy a ``src`` directory to ``dst``.
#
#    Recursively copies files and subdirectories from ``src`` to ``dst``,
#    optionally excluding and/or changing the names of files and subdirectories
#    based upon the function ``xform_fn``.
#
#    ``xform_fn``, if given, should be a function that meets the following
#    criteria:
#        1. It takes three strings as parameters: ``src_base``, ``src_dirname``,
#           and ``src_basename``.
#        2. If the given source filespec is to be copied, a single string should
#           be returned.  This string will be the desired pathname of the
#           destination file or directory.
#        3. If the given source filespec should NOT be copied, then ``None``
#           must be returned.  Note that if ``None`` is returned for a source
#           filespec that represents a directory, pycopy will not recurse into
#           that directory.
#
#    """
#    todo = collections.deque( [ DirEntry(src, '', x) for x in os.listdir(src) ] )
#        
#    while len(todo) > 0:
#        x = todo.pop()
#        #if xform_fn(src, x['dirname'], x['basename']) == None:
#        #    continue
#        if x.is_dir():
#            ###################################################################
#            #
#            # Skip over this directory if xform_fn wants us to.
#            #
#            xformed_name = xform_fn(x.src_dir, x.src_subdir, x.basename)
#            if xformed_name is None:
#                continue
#            #
#            ###################################################################
#            ###################################################################
#            #
#            # Add all children to the "todo" queue.
#            #
#            for y in os.listdir(
#                os.path.join(x.src_dir, x.src_subdir, x.basename)
#            ):
#                todo.append(
#                    DirEntry(
#                        x.src_dir, 
#                        os.path.join(x.src_subdir, x.basename),
#                        y
#                    )
#                )
#            #
#            ###################################################################
#            ###################################################################
#            #
#            # Create the destination directory if it does not already exist.
#            #
#            if not os.path.exists(xformed_name):
#                os.makedirs(xformed_name)
#            #
#            ###################################################################
#        else:
#            xformed_name = xform_fn(x.src_dir, x.src_subdir, x.basename)
#            if xformed_name is None:
#                continue
#
#            # # NOTE: This version of determining if the file should be copied
#            # #       might ignore case if the dst is a case-insensitive file
#            # #       system.
#            #
#            #try:
#            #    if not should_copy(x.stat, os.stat(xformed_name)):
#            #        continue
#            #except OSError, e:
#            #    if e.errno == 2:
#            #        pass
#            
#            if (
#                os.path.exists(xformed_name)
#                and not should_copy(x.stat, os.stat(xformed_name))
#            ):
#                continue
#
#            copy_fn(os.path.join(x.src_dir, x.src_subdir, x.name), xformed_name)
#
#def pycopy(
#    src, dst, 
#    copy_fn=shutil.copy,
#    xform_fn=lambda src_base, src_dirname, src_basename: src_basename,
#    _dbg_scandir_fn=_SCANDIR_FN
#):
#    todo = collections.deque(_dbg_scandir_fn(src))
#        
#    while len(todo) > 0:
#        x = todo.pop()
#        #if xform_fn(src, x['dirname'], x['basename']) == None:
#        #    continue
#        if x.is_dir():
#            for y in _dbg_scandir_fn(os.path.join(x.path, x.name)):
#                todo.append(y)
#        else:
#            xformed_name = xform_fn(src, x.path, x.name)
#            if xformed_name is None:
#                #if os.path.exists(filespec):
#                #    os.remove(filespec)
#                continue
#            if should_copy(x.stat, os.stat(xformed_name))
#            copy_fn(os.path.join(x.path, x.name), xformed_name)



