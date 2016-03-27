# coding=utf-8
from __future__ import absolute_import

try:
    from gzip import compress, decompress
except ImportError:
    from io import BytesIO
    from gzip import GzipFile


    def compress(bs):
        outf = BytesIO()
        with GzipFile(fileobj=outf, mode='wb') as g:
            g.write(bs)
        return outf.getvalue()


    def decompress(bs):
        inf = BytesIO(bs)
        with GzipFile(fileobj=inf, mode='rb') as g:
            return g.read()
