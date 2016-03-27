# coding=utf-8
from __future__ import absolute_import

from os import path

from crumhorn.platform.compatibility import tempfile


def test_temp_directory_creates_directory():
    with tempfile.TemporaryDirectory() as f:
        assert path.exists(f)
        assert path.isdir(f)


def test_temp_directory_gets_cleaned_up():
    with tempfile.TemporaryDirectory() as f:
        assert path.exists(f)

    assert not path.exists(f)


def test_temp_directory_respects_prefix_and_suffix():
    with tempfile.TemporaryDirectory(prefix='test_prefix', suffix='test_suffix') as f:
        assert path.basename(f).startswith('test_prefix')
        assert path.basename(f).endswith('test_suffix')


def test_temp_directory_respects_dir_arg():
    with tempfile.TemporaryDirectory() as parent:
        with tempfile.TemporaryDirectory(dir=parent) as child:
            assert path.relpath(child, parent) == path.basename(child)
