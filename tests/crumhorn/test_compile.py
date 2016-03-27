# coding=utf-8
from __future__ import absolute_import
import shutil

import pytest

from crumhorn.compile import *
from crumhorn.configuration import machineconfiguration
from crumhorn.configuration.environment import machinespec_repository
from crumhorn.platform.compatibility import fileinput

_here = path.dirname(__file__)
_raw_configuration = path.abspath(path.join(_here, 'configuration', 'raw_configuration'))
_raw_configuration_missing_files = path.abspath(path.join(_here, 'configuration_with_missing_file'))
_raw_configuration_unbundled_parent = path.abspath(path.join(_here, 'configuration_with_unbundled_parent'))


def test_compilation_results_in_file_that_can_be_read_by_configuration_parser(tmpdir):
    target = tmpdir.join('compiled_output.crumhorn').strpath
    compile_folder(source=_raw_configuration, output=target)
    assert machineconfiguration.load_configuration(target) is not None


def test_will_throw_when_files_are_missing_from_config(tmpdir):
    target = tmpdir.join('compiled_output.crumhorn').strpath
    with pytest.raises(MissingDataFileError):
        compile_folder(source=_raw_configuration_missing_files, output=target)


def test_hash_changes_when_content_changes(tmpdir):
    target = tmpdir.join('compiled_output.crumhorn').strpath
    compile_folder(source=_raw_configuration, output=target)
    original = machineconfiguration.load_configuration(target)

    new_config_path = tmpdir.join('changed')
    shutil.copytree(_raw_configuration, new_config_path.strpath)
    new_unchanged_output_path = tmpdir.join('unchanged.crumhorn').strpath
    compile_folder(new_config_path.strpath, new_unchanged_output_path)
    new_unchanged = machineconfiguration.load_configuration(new_unchanged_output_path)
    assert original.config_hash == new_unchanged.config_hash

    with new_config_path.join('horn.toml').open('a') as f:
        f.writelines(['\n\t', '\t\n'])  # any change to the file
    new_changed_output_path = tmpdir.join('changed.crumhorn').strpath
    compile_folder(new_config_path.strpath, new_changed_output_path)
    new_changed = machineconfiguration.load_configuration(new_changed_output_path)
    assert original.config_hash != new_changed.config_hash


def test_base_package_is_bundled(tmpdir):
    child_package_source = tmpdir.join('child_package').strpath
    shutil.copytree(_raw_configuration, child_package_source)
    with fileinput.input(path.join(child_package_source, 'horn.toml'), inplace=True) as child_config:
        for line in child_config:
            if line.startswith('name'):
                print('name = "childname"')
            elif line.startswith('base_image'):
                continue
            else:
                print(line)

    parent_machine_spec = tmpdir.join('parent.crumspec').strpath
    compile_folder(_raw_configuration, parent_machine_spec)

    child_machine_spec = tmpdir.join('child.crumspec').strpath
    compile_folder(child_package_source, child_machine_spec, base_package=parent_machine_spec)

    result = machineconfiguration.load_configuration(child_machine_spec)
    assert result.name == 'childname'
    assert result.base_image_configuration.name == 'raw_configuration'


def test_parent_package_is_looked_up_in_repository(tmpdir):
    repository = machinespec_repository.MachineSpecRepository(environment={'repository.searchpath': tmpdir.strpath})
    parent_file = tmpdir.join('raw_configuration.crumspec').strpath
    compile_folder(source=_raw_configuration, output=parent_file)

    child_file = tmpdir.join('child.crumspec').strpath
    compile_folder(
        source=_raw_configuration_unbundled_parent,
        output=child_file,
        machinespec_repository=repository)
