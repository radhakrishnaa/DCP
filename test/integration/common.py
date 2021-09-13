# common.py  -- common functions

import inspect
import sys


SHOW_DEBUG = False

def debug(msg, prefix=""):
    if SHOW_DEBUG:
        print "%sDEBUG: %s" % (prefix, msg)

def info(msg, prefix=""):
    print "%sINFO: %s" % (prefix, msg)

def warn(msg, prefix=""):
    print "%sWARNING: %s" % (prefix, msg)

def error(msg, abort=True, prefix=""):
    if abort:
        raise RuntimeError("%sERROR: %s" % (prefix, msg))
    else:
        print "%sERROR: %s" % (prefix, msg)

def enum(*sequential, **named):
    """Create pseudo-enumaration
         usage: Numbers = enum('ZERO', 'ONE', 'TWO'); Numbers.ONE => 1
         usage: ReturnCodes = enum(RC_OK=0, RC_WAIT=100); ReturnCodes.RC_OK => 0
    """
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)


def get_function_name():
    """Return the calling function's name"""
    return inspect.stack()[1][3]

def get_function_docstring(funcname):
    """Return the docstring of the given function name"""
    return globals()[funcname].__doc__

