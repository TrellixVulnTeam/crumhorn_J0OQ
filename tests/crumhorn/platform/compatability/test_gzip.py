# coding=utf-8
from __future__ import absolute_import

from crumhorn.platform.compatibility import gzip


def test_gzip_can_compress_and_decompress_data_to_same_result():
    compressed = gzip.compress(b'hello world')
    decompressed = gzip.decompress(compressed)

    assert decompressed == b'hello world'
