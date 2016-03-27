# coding=utf-8

from crumhorn.configuration.environment import machinespec_repository


def test_can_find_machine_spec_from_search_path(tmpdir):
    path_to_crumspec = tmpdir.join('machinespec.crumspec')
    path_to_crumspec.write('any data')
    repository = machinespec_repository.MachineSpecRepository(environment={'repository.searchpath': tmpdir.strpath})
    assert repository.find_machine_spec(
        machinespec_repository.MachineSpecIdentifier('machinespec')) == path_to_crumspec.strpath
