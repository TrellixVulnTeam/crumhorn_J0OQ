# coding=utf-8
import base64
import hashlib
import os
import re
import sys
import tarfile
from os import path
from tempfile import NamedTemporaryFile

from crumhorn.configuration import machineconfiguration

_missing_data_pattern = re.compile('filename \'(?P<filename>[^\']+)\' not found')


class MissingDataFileError(RuntimeError):
    pass


def compile_folder(source, output):
    source = path.abspath(source)
    output = path.abspath(output)
    with tarfile.open(output, mode='w:xz') as dest:
        lock_hash = hashlib.sha512()
        for dirpath, dirs, files in os.walk(source, followlinks=True):
            # these sorts ensure stable hashing for unchanged content
            dirs[:] = sorted(dirs)
            for f in sorted(files):
                f_path = path.join(dirpath, f)
                with open(f_path, 'rb') as opened:
                    lock_hash.update(opened.read())

                file_to_add = path.abspath(f_path)
                dest_location = path.relpath(file_to_add, source)
                dest.add(file_to_add, arcname=dest_location)

        with NamedTemporaryFile(mode='wb') as lock_file:
            lock = base64.urlsafe_b64encode(lock_hash.digest())
            lock_file.file.write(lock)
            lock_file.file.close()
            dest.add(lock_file.name, arcname='lock')

    try:
        result = machineconfiguration.load_configuration(output)
    except KeyError as e:
        for a in e.args:
            missing_file_match = _missing_data_pattern.search(a)
            if missing_file_match:
                raise MissingDataFileError(missing_file_match.group('filename'))


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    compile_folder(argv[0], argv[1])


if __name__ == '__main__':
    main()
