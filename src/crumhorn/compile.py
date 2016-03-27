# coding=utf-8
"""
    crumhorn configuration bundler.

    Raw configurations ("package specification") are read in, and bundled into a "Machine Spec", which can be handled by the other crumhorn tools (e.g. prepare and launch)

    Usage:
        compile <package> [--from=<base_configuration>]
        compile <package> <destination> [--from=<base_configuration>]

    Arguments:
        <package>                       The folder containing your package specification. This is where your horn.toml
                                        lives.
        <destination>                   The destination for your bundled Machine Spec.

    Options:
        --from <base_configuration>     An already-compiled Machine Spec. If specified, when this package is prepared,
                                        then first boot will be from a snapshot of that package, rather than a raw image.

"""

import base64
import hashlib
import os
import re
import sys
import tarfile
from os import path
from tempfile import NamedTemporaryFile, TemporaryDirectory

import docopt

from crumhorn.configuration import machineconfiguration

_missing_data_pattern = re.compile('filename \'(?P<filename>[^\']+)\' not found')


class MissingDataFileError(RuntimeError):
    pass


def compile_folder(source, output, base_package=None):
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

        if base_package is not None:
            with TemporaryDirectory() as tempdir:
                with tarfile.open(base_package, mode='r:xz') as base:
                    base.extractall(path=tempdir)
                    with open(path.join(tempdir, 'horn.toml'), 'rb') as base_hash:
                        lock_hash.update(base_hash.read())
                dest.add(tempdir, arcname='base')

        with NamedTemporaryFile(mode='wb') as lock_file:
            lock = base64.urlsafe_b64encode(lock_hash.digest())
            lock_file.file.write(lock)
            lock_file.file.close()
            dest.add(lock_file.name, arcname='lock')

    # Check the resultant machinespec can load
    try:
        result = machineconfiguration.load_configuration(output)
    except KeyError as e:
        for a in e.args:
            missing_file_match = _missing_data_pattern.search(a)
            if missing_file_match:
                raise MissingDataFileError(missing_file_match.group('filename'))


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    options = docopt.docopt(__doc__, argv=argv)
    source = options['<package>']
    dest = options['<destination>']
    if not dest:
        dest = path.basename(source) + '.crumspec'
    base_package = options['--from']
    compile_folder(source, dest, base_package)



if __name__ == '__main__':
    main()
