import os
import time
from functools import lru_cache
from droplet import Droplet
import digitalocean

with open('user-data', 'r') as f:
	userdata = f.read()

with open(os.path.join(os.path.expanduser('~'), '.ssh', 'id_rsa.pub'), 'r') as f:
	ssh_key = f.read()

def create_droplet():
	droplet = digitalocean.Droplet(token=os.environ['digitaloceantoken'],
		name='example',
		region='lon1',
		image='fedora-23-x64',
		size_slug='512mb',
		backups=False,
		ssh_keys=['f3:40:16:64:d2:ff:0c:d2:62:20:e4:57:de:d8:62:8e'],
		user_data=userdata)

	droplet.create()
	return Droplet(droplet)

if __name__ == '__main__':
	droplet = create_droplet()
	print('Creating...', end='')
	while not droplet.is_up():
		print('.', end='')
		time.sleep(2)
	print()
	print('Droplet created: {ip}'.format(ip=droplet.ip))

