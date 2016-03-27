# coding=utf-8
import base64
import gzip
import itertools


def as_userdata_string(machine_configuration):
    return '\n'.join(itertools.chain(['#cloud-config'], _as_userdata_parts(machine_configuration)))


def _titled_list(list_name, items):
    if not items: return

    yield '{}:'.format(list_name)
    for i in items:
        yield '  - {}'.format(i)


def _file_as_byte_echo(file):
    return 'echo \'{encoded_content}\' | base64 -d | gzip -d > {target_file}' \
        .format(
        encoded_content=base64.standard_b64encode(gzip.compress(file.content)).decode('utf-8'),
        target_file=file.target_path)


def _as_userdata_parts(machine_configuration):
    if machine_configuration is None:
        return

    try:
        required_packages = machine_configuration.required_packages
    except AttributeError:
        required_packages = []

    yield from _titled_list('packages', required_packages)

    try:
        files_to_copy = machine_configuration.files
    except AttributeError:
        files_to_copy = []
    file_copy_commands = [_file_as_byte_echo(f) for f in files_to_copy] + [
        'chmod +x {target_path}'.format(target_path=f.target_path) for f in files_to_copy if 'executable' in f.flags]

    try:
        raw_cmds = machine_configuration.raw_commands or []
    except AttributeError:
        raw_cmds = []

    try:
        services = machine_configuration.services or []
    except AttributeError:
        services = []
    service_cmds = ['systemctl enable {name}'.format(name=s.name) for s in services] + \
                   ['systemctl start {name}'.format(name=s.name) for s in services if s.requires_start] + \
                   ['systemctl restart {name}'.format(name=s.name) for s in services if s.requires_restart]

    yield from _titled_list('runcmd', itertools.chain(file_copy_commands, raw_cmds, service_cmds, ['shutdown +1']))
