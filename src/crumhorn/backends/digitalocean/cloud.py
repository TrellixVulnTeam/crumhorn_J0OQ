# coding=utf-8
import datetime
import random
import string

import digitalocean

import crumhorn.configuration.userdata as userdata
from crumhorn.keyutil import get_fingerprint
from .droplet import Droplet


def _generate_new_droplet_name(machine_configuration):
    return '{config_name}-{when}-{rand}'.format(
        config_name=machine_configuration.name,
        when=datetime.datetime.now().strftime('%Y%m%d%H%m'),
        rand=''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10)))


class Cloud():
    def __init__(self, authentication_token, region_name, root_ssh_key_fingerprint):
        self.root_ssh_key_fingerprint = root_ssh_key_fingerprint
        self.region_name = region_name
        self.authentication_token = authentication_token
        self._manager_api = digitalocean.Manager(token=authentication_token)

    def find_base_snapshot_name(self, machine_configuration):
        if isinstance(machine_configuration, type('')) or isinstance(machine_configuration, type(b'')):
            return machine_configuration
        else:
            return '{name}-{region}-{hash}'.format(name=machine_configuration.name, region=self.region_name,
                                                   hash=machine_configuration.config_hash.decode('utf-8'))

    def first_boot(self, machine_configuration, size_slug):

        configuration = str(userdata.as_userdata_string(machine_configuration))

        droplet = digitalocean.Droplet(token=self.authentication_token,
                                       name=machine_configuration.name,
                                       region=self.region_name,
                                       image=self.find_image_id(machine_configuration.base_image_configuration),
                                       size_slug=size_slug,
                                       backups=False,
                                       ssh_keys=[self.root_ssh_key_fingerprint],
                                       user_data=configuration)

        droplet.create()
        return Droplet(self, droplet, machine_configuration)

    def launch(self, machine_configuration, size_slug):
        snapshot_id = self.find_image_id(machine_configuration)

        droplet = digitalocean.Droplet(token=self.authentication_token,
                                       name=_generate_new_droplet_name(machine_configuration),
                                       region=self.region_name,
                                       image=snapshot_id,
                                       size_slug=size_slug,
                                       backups=False,
                                       ssh_keys=[self.root_ssh_key_fingerprint],
                                       user_data=None)

        droplet.create()
        return Droplet(self, droplet, machine_configuration)

    def find_image_id(self, machine_configuration):
        snapshot_name = self.find_base_snapshot_name(machine_configuration)
        snapshots = {s.name: s for s in self._manager_api.get_my_images()}
        try:
            return snapshots[snapshot_name].id
        except KeyError:
            pass

        distributions = {i.slug: i for i in self._manager_api.get_images(type='distribution')}
        try:
            return distributions[snapshot_name].id
        except KeyError:
            raise KeyError('No snapshot named {}'.format(snapshot_name))


def initialize_cloud(environment):
    return Cloud(
        authentication_token=environment['digitaloceantoken'],
        region_name='lon1',
        root_ssh_key_fingerprint=get_fingerprint(environment['ssh_key']))
