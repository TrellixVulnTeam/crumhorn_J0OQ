# coding=utf-8
from __future__ import print_function
def _print_no_buffer(*args, **kwargs):
    import sys
    print(*args, **kwargs)
    sys.stdout.flush()


class UncertainProgressBar():
    def __init__(self, label=None):
        self.label = label

    def __enter__(self):
        _print_no_buffer(self.label or '.', end='')
        return self

    def tick(self):
        _print_no_buffer('.', end='')

    def __exit__(self, exc_type, exc_val, exc_tb):
        print()
        return False
