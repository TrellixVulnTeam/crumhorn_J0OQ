#! /usr/bin/env python3
# coding=utf-8
import os
import time

import digitalocean

from . import UncertainProgressBar
from .backends.droplet import Droplet
from .keyutil import get_fingerprint


def construct_cloudinit_userdata():
    header = '#cloud-config'
    with open('users.config', 'r') as f:
        users_config = f.read()

    with open('box.config', 'r') as f:
        box_config = f.read()

    return '\n'.join([header, users_config, box_config])


with open(os.path.join(os.path.expanduser('~'), '.ssh', 'id_rsa.pub'), 'r') as f:
    ssh_key_raw = f.readline()
    ssh_key = get_fingerprint(ssh_key_raw)


def create_droplet():
    user_data = construct_cloudinit_userdata()
    with open('user-data', 'w') as f:
        f.write(user_data)

    droplet = digitalocean.Droplet(token=os.environ['digitaloceantoken'],
                                   name='example',
                                   region='lon1',
                                   image='fedora-23-x64',
                                   size_slug='512mb',
                                   backups=False,
                                   ssh_keys=[ssh_key],
                                   user_data=user_data)

    droplet.create()
    return Droplet(droplet)


def main():
    with UncertainProgressBar('Creating droplet...') as p:
        droplet = create_droplet()
        while not droplet.is_up():
            p.tick()
            time.sleep(2)

    print('Droplet created: {ip}'.format(ip=droplet.ip))


if __name__ == '__main__':
    main()
