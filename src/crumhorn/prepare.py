#! /usr/bin/env python3
# coding=utf-8
import os
import sys
import time

import crumhorn.configuration.machineconfiguration as machineconfiguration
from crumhorn.backends.digitalocean import cloud
from . import UncertainProgressBar


def create_droplet(manager, config_path):
    return manager.first_boot(
        machine_configuration=machineconfiguration.load_configuration(config_path),
        size_slug='512mb')


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    configuration = argv[0]

    manager = cloud.initialize_cloud(os.environ)

    with UncertainProgressBar('Creating droplet...') as p:
        droplet = create_droplet(manager, configuration)
        while not droplet.is_up():
            p.tick()
            time.sleep(2)

    with UncertainProgressBar('Awaiting power down...') as p:
        while not droplet.is_powered_down():
            p.tick()
            time.sleep(2)

    snapshot_name, action = droplet.snapshot()
    with UncertainProgressBar('Taking droplet snapshot...') as p:
        while not action.is_finished():
            p.tick()
            time.sleep(2)

    with UncertainProgressBar('Tearing down base image...') as p:
        droplet.delete()

    print('Droplet preparation finished - snapshot saved as {}'.format(snapshot_name))


if __name__ == '__main__':
    main()
