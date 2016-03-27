# coding=utf-8
import tarfile

import toml


class DerivedMachineConfiguration:
    def __init__(self,
                 name,
                 base_image_configuration,
                 config_hash,
                 raw_commands=None,
                 required_packages=None,
                 services=None,
                 files=None):

        if services is None:
            services = []
        if files is None:
            files = []
        if required_packages is None:
            required_packages = []
        if raw_commands is None:
            raw_commands = []

        self.name = name
        self.base_image_configuration = base_image_configuration
        self.raw_commands = raw_commands
        self.config_hash = config_hash
        self.required_packages = required_packages
        self.services = services
        self.files = files


class FileToCopy:
    def __init__(self, content, target_path, flags=None):
        if flags is None:
            flags = []

        self.content = content
        self.target_path = target_path
        self.flags = flags


class ServiceConfig:
    def __init__(self, service_name, flags=None):
        if flags is None:
            flags = []
        self.name = service_name
        self.flags = flags

    @property
    def requires_restart(self):
        return 'restart' in self.flags

    @property
    def requires_start(self):
        return 'restart' not in self.flags


def _file_to_copy_from_config(filespec, configuration_file, path_prefix=''):
    return FileToCopy(
        content=configuration_file.extractfile(
            '{prefix}{localspec}'.format(
                prefix=path_prefix,
                localspec=filespec['local'])).read(),
        target_path=filespec['remote'],
        flags=(flag for flag in ('executable',) if filespec.get('executable', None)))


def _read_config(configuration_file, path_prefix):
    horn_toml = configuration_file.extractfile('{}horn.toml'.format(path_prefix))
    horn_config = toml.loads(horn_toml.read().decode('utf-8'))

    machine_configuration_name = horn_config['horn']['name']
    machine_config = horn_config.get(machine_configuration_name, None)
    if machine_config:
        machine_configuration_raw_commands = horn_config[machine_configuration_name].get('raw_commands', [])
        machine_requires_packages = horn_config[machine_configuration_name].get('requires', [])
        machine_files = []
        machine_files_config = horn_config[machine_configuration_name].get('files', [])
        for filespec in machine_files_config:
            machine_files.append(_file_to_copy_from_config(filespec, configuration_file, path_prefix))

        machine_services = []
        machine_services_config = horn_config[machine_configuration_name].get('services', {})
        for name, service_spec in machine_services_config.items():
            try:
                machine_services.append(ServiceConfig(name, flags=(k for k, v in service_spec.items() if v)))
            except AttributeError:
                machine_services.append(ServiceConfig(name))

    else:
        machine_configuration_raw_commands = []
        machine_requires_packages = []
        machine_files = []
        machine_services = []

    parent_prefix = '{}base/'.format(path_prefix)
    try:
        base_image_configuration = _read_config(configuration_file, path_prefix=parent_prefix)
    except KeyError as e:
        if 'filename \'{parent_prefix}horn.toml\' not found'.format(parent_prefix=parent_prefix) in e.args:
            base_image_configuration = horn_config['horn']['base_image']
        else:
            raise

    hash_file = configuration_file.extractfile('{}lock'.format(path_prefix))
    config_hash = hash_file.read()

    return DerivedMachineConfiguration(machine_configuration_name, base_image_configuration, config_hash,
                                       machine_configuration_raw_commands, machine_requires_packages,
                                       files=machine_files, services=machine_services)


def load_configuration(path):
    with tarfile.open(path, 'r:gz') as configuration_file:
        return _read_config(configuration_file, '')
