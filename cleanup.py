import os

from droplet import Droplet
import digitalocean

def find_all_droplets():
	manager = digitalocean.Manager(token=os.environ['digitaloceantoken'])
	for d in manager.get_all_droplets():
		yield Droplet(d)

if __name__ == '__main__':
	for droplet in find_all_droplets():
		droplet.delete()

