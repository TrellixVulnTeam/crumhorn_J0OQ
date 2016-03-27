# coding=utf-8
import base64

from crumhorn.configuration.userdata import as_userdata_string
from crumhorn.platform.compatibility import gzip


class SimpleFileForCopyingRemote():
    def __init__(self, content, target_path, flags=None):
        if flags is None:
            flags = []

        self.content = content
        self.target_path = target_path
        self.flags = flags


class SimpleMachineConfiguration():
    def __init__(self, raw_commands=None, required_packages=None, files=None, services=None):
        self.raw_commands = raw_commands or []
        self.required_packages = required_packages or []
        self.files = files or []
        self.services = services or []


class SimpleServiceConfig:
    def __init__(self, name, requires_restart=False, requires_start=True):
        self.name = name
        self.requires_restart = requires_restart
        self.requires_start = requires_start


def test_outputs_raw_commands_as_yaml_items():
    assert '''runcmd:
  - cmd1 with args
  - cmd2
  - cmd3
''' in as_userdata_string(
        SimpleMachineConfiguration(raw_commands=['cmd1 with args', 'cmd2', 'cmd3'], required_packages=None))


def test_shuts_down_machine_when_done():
    empty_config = SimpleMachineConfiguration()
    result = as_userdata_string(empty_config)
    assert result.endswith('shutdown +1')


def test_starts_with_cloud_config_header():
    result = as_userdata_string(SimpleMachineConfiguration(None, None))
    assert result.startswith("#cloud-config")


def test_adds_required_packages():
    assert '''packages:
  - super_service
''' in as_userdata_string(SimpleMachineConfiguration(raw_commands=[], required_packages=['super_service']))


def test_adds_required_packages_before_runcmd_section():
    result = as_userdata_string(SimpleMachineConfiguration(raw_commands=['cmd1'], required_packages=['package1']))
    assert result.index('packages:') < result.index('runcmd:')


def test_adds_file_copy_steps_before_other_runcmds():
    configuration = SimpleMachineConfiguration(raw_commands=['cmd1'],
                                               files=[SimpleFileForCopyingRemote(b'content', '/etc/something.conf')])
    result = as_userdata_string(configuration)
    assert result.index('cmd1') > result.index('/etc/something.conf')


def test_file_copy_steps_are_gzip_and_b64_encoded():
    configuration = SimpleMachineConfiguration(raw_commands=['cmd1'],
                                               files=[SimpleFileForCopyingRemote(b'content', '/etc/something.conf')])
    result = as_userdata_string(configuration)
    line_with_file_copy = [l for l in result.split('\n') if '/etc/something.conf' in l][0]
    content = line_with_file_copy[len('  - echo \''):line_with_file_copy.find('\' |')]
    result = gzip.decompress(base64.standard_b64decode(content))

    assert result == b'content'
    assert 'gzip -d ' in line_with_file_copy
    assert 'base64 -d ' in line_with_file_copy


def test_files_marked_with_executable_flags_if_they_were_configured_for_them():
    configuration = SimpleMachineConfiguration(raw_commands=['cmd1'],
                                               files=[
                                                   SimpleFileForCopyingRemote(b'content', '/usr/bin/runnable',
                                                                              flags=['executable']),
                                                   SimpleFileForCopyingRemote(b'content', '/usr/bin/not_runnable')
                                               ])
    result = as_userdata_string(configuration)

    assert 'chmod +x /usr/bin/runnable' in result
    assert 'chmod +x /usr/bin/not_runnable' not in result


def test_services_are_enabled_and_stared():
    configuration = SimpleMachineConfiguration(services=[SimpleServiceConfig('sshd')])

    result = as_userdata_string(configuration)

    assert 'systemctl enable sshd' in result
    assert 'systemctl start sshd' in result


def test_service_installation_come_after_raw_commands():
    configuration = SimpleMachineConfiguration(services=[SimpleServiceConfig('sshd')], raw_commands=['cmd1'])

    result = as_userdata_string(configuration)

    assert result.index('sshd') > result.index('cmd1')


def test_services_requiring_restart_come_after_raw_commands():
    configuration = SimpleMachineConfiguration(services=[SimpleServiceConfig('sshd', requires_restart=True)],
                                               raw_commands=['cmd1'])

    result = as_userdata_string(configuration)

    assert 'systemctl restart sshd' in result
    assert result.index('restart') > result.index('cmd1')


def test_services_not_requiring_start_are_not_started():
    configuration = SimpleMachineConfiguration(services=[SimpleServiceConfig('sshd', requires_start=False)])

    result = as_userdata_string(configuration)

    assert 'systemctl start sshd' not in result
