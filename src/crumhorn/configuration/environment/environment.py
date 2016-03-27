# coding=utf-8
import os

from crumhorn.configuration.environment import machinespec_repository


class CrumhornEnvironment:
    def __init__(self, machinespec_repository, cloud_config):
        self.cloud_config = cloud_config
        self.machinespec_repository = machinespec_repository


def build_environment():
    machinespec_repo = machinespec_repository.MachineSpecRepository(
        {'repository.searchpath': ':'.join([os.getcwd(), os.environ.get('crumhorn.repository.searchpath', '')])})
    cloud_config = {'digitaloceantoken': os.environ['digitaloceantoken']}
    return CrumhornEnvironment(machinespec_repo, cloud_config)
