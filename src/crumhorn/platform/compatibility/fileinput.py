# coding=utf-8
from __future__ import absolute_import

import fileinput as _fileinput

try:
    # noinspection PyStatementEffect
    _fileinput.FileInput.__exit__
    from fileinput import *
except AttributeError:
    class FileInput(_fileinput.FileInput):
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.close()


    input = FileInput
