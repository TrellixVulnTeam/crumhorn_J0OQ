# coding=utf-8
import os
import tarfile
import tempfile
from os import path

import crumhorn.configuration.machineconfiguration as machineconiguration

_here = os.path.dirname(__file__)
_raw_configuration = path.abspath(os.path.join(_here, 'raw_configuration'))
_raw_configuration_with_parent = path.abspath(os.path.join(_here, 'raw_configuration_with_parent'))


def loading_as_package(folder_to_package):
    with tempfile.NamedTemporaryFile(mode='w') as package_file:
        package_file.close()
        with tarfile.open(name=package_file.name, mode='w:gz') as package:
            for dirpath, dirnames, fnames in os.walk(folder_to_package):
                for f in fnames:
                    abspath = path.join(dirpath, f)
                    package.add(abspath, arcname=path.relpath(abspath, folder_to_package))

        result = machineconiguration.load_configuration(package_file.name)
    return result


def test_can_read_basic_configuration():
    result = loading_as_package(_raw_configuration)

    assert result.name == 'raw_configuration'
    assert result.base_image_configuration == 'fedora-23-x64'
    assert result.required_packages == ['nftables']
    assert result.raw_commands == ['echo hello world']


def test_can_include_services_to_enable_from_configuration():
    result = loading_as_package(_raw_configuration)

    assert set(s.name for s in result.services) == {'sshd', 'firewalld'}


def test_can_set_services_for_restart():
    result = loading_as_package(_raw_configuration)

    assert set(s.name for s in result.services if s.requires_restart) == {'sshd'}


def test_can_load_local_files_to_send_remotely():
    result = loading_as_package(_raw_configuration)

    assert len(result.files) > 0
    with open(path.join(_raw_configuration, 'local_files', 'extra_configuration'), 'rb') as extra_file:
        target = extra_file.read()
    assert any([f.content == target for f in result.files])


def test_local_files_can_be_marked_executable():
    result = loading_as_package(_raw_configuration)

    assert any(['executable' in f.flags for f in result.files])


def test_service_requires_start_by_default():
    result = loading_as_package(_raw_configuration)

    assert any([s.requires_start for s in result.services if s.name == 'firewalld'])


def test_services_requiring_restart_dont_require_start():
    result = loading_as_package(_raw_configuration)

    assert not any([s.requires_start for s in result.services if s.name == 'sshd'])


def test_parent_configuration_can_have_nested_files():
    result = loading_as_package(_raw_configuration_with_parent)
    assert len(result.base_image_configuration.files) > 0


def first(gen):
    for g in gen:
        return g
