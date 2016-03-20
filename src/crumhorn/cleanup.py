#! /usr/bin/env python3
import os

from .backends.droplet import Droplet
import digitalocean

def find_all_droplets():
	manager = digitalocean.Manager(token=os.environ['digitaloceantoken'])
	for d in manager.get_all_droplets():
		yield Droplet(d)

def main():
	for droplet in find_all_droplets():
		droplet.delete()

if __name__ == '__main__':
	main()