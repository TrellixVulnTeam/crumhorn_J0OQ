# coding=utf-8
import shutil

import pytest

from crumhorn.compile import *
from crumhorn.configuration import machineconfiguration

_here = path.dirname(__file__)
_raw_configuration = path.abspath(path.join(_here, 'configuration', 'raw_configuration'))
_raw_configuration_missing_files = path.abspath(path.join(_here, 'configuration_with_missing_file'))


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
