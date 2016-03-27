# coding=utf-8
from __future__ import absolute_import
# noinspection PyUnresolvedReferences
from tempfile import *

try:
    from tempfile import TemporaryDirectory
except ImportError:
    import tempfile
    import shutil


    class TemporaryDirectory(object):
        def __init__(self, suffix='', prefix='tmp', dir=None):
            self.dir = dir
            self.suffix = suffix
            self.prefix = prefix

        def __enter__(self):
            self._path = tempfile.mkdtemp(suffix=self.suffix, prefix=self.prefix, dir=self.dir)
            return self._path

        def __exit__(self, exc_type, exc_val, exc_tb):
            shutil.rmtree(self._path)
