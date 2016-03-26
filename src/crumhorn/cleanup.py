#! /usr/bin/env python3
# coding=utf-8
import os

import digitalocean

from . import UncertainProgressBar
from .backends.droplet import Droplet


def find_all_droplets():
    manager = digitalocean.Manager(token=os.environ['digitaloceantoken'])
    for d in manager.get_all_droplets():
        yield Droplet(d)


def main():
    with UncertainProgressBar('Deleting droplets...') as p:
        for droplet in find_all_droplets():
            droplet.delete()
            p.tick()


if __name__ == '__main__':
    main()
