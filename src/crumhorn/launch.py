# coding=utf-8
import os
import sys
import time

import crumhorn.configuration.machineconfiguration as machineconfiguration
from crumhorn.backends.digitalocean import cloud
from . import UncertainProgressBar


def launch_droplet(manager, config_path):
    return manager.launch(
        machine_configuration=machineconfiguration.load_configuration(config_path),
        size_slug='512mb')


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    configuration = argv[0]

    manager = cloud.initialize_cloud(os.environ)

    with UncertainProgressBar('Creating droplet...') as p:
        droplet = launch_droplet(manager, configuration)
        while not droplet.is_up():
            p.tick()
            time.sleep(2)

    print('Droplet created: {ip}'.format(ip=droplet.ip))


if __name__ == '__main__':
    main()
