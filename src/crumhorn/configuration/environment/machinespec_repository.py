# coding=utf-8
from os import path


class MachineSpecIdentifier:
    def __init__(self, name, namespace=None, version=None):
        self.namespace = namespace
        self.name = name
        self.version = version

    @classmethod
    def from_string(cls, string):
        return MachineSpecIdentifier(string)


class MachineSpecRepository:
    def __init__(self, environment):
        self._search_path = environment['repository.searchpath'].split(':')

    def find_machine_spec(self, machinespec_identifier):
        if isinstance(machinespec_identifier, type('')):
            machinespec_identifier = MachineSpecIdentifier.from_string(machinespec_identifier)

        for search_path in self._search_path:
            candidate_path = path.join(search_path, machinespec_identifier.name + '.crumspec')
            if path.exists(candidate_path):
                return candidate_path
