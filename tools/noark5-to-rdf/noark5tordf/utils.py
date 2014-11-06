#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,errno

def is_sequence(arg):
    """ Checks if "arg" is a proper sequence or not (i.e. list, tuple..) """
    return not hasattr(arg, "strip") and (hasattr(arg, "__getitem__") or hasattr(arg, "__iter__"))


def assertDir(path, rootdir=None):
    """ Make sure the given directory/ies exists in the given or current path """

    if is_sequence(path):
        for p in path:
            assertDir(p, rootdir=rootdir)
    else:
        if not rootdir:
            rootdir = os.path.realpath(os.path.curdir)

        if not os.path.isabs(path):
            path = rootdir + os.sep + path
        
        if os.path.isdir(path):
            return

        # python 2.x is stupid.
        try:
            os.makedirs(path)
        except OSError as exc: # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(rootdir + os.sep + path):
                pass
            else:
                raise


def _xmlcharref_encode(unicode_data, encoding="ascii"):
    """Emulate Python 2.3's 'xmlcharrefreplace' encoding error handler."""
    res = ""

    # Step through the unicode_data string one character at a time in
    # order to catch unencodable characters:
    for char in unicode_data:
        try:
            char.encode(encoding, 'strict')
        except UnicodeError:
            if ord(char) <= 0xFFFF:
                res += '\\u%04X' % ord(char)
            else:
                res += '\\U%08X' % ord(char)
        else:
            res += char

    return res


def escape_literal(literal):
    """ Escape the string literal as per NTriples rules """
    literal = literal.replace('\\', '\\\\').replace('\n', '\\n').replace('"', '\\"').replace('\r', '\\r').replace('\v', '')
    literal = _xmlcharref_encode(literal, "ascii")
    return literal



def getCurrDir():
    """ Get the current directory """
    return os.path.realpath(os.path.curdir)

