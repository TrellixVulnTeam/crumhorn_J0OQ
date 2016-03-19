from functools import lru_cache

class Droplet(object):
	def __init__(self, _droplet_api):
		self._droplet_api = _droplet_api

	@property
	@lru_cache(maxsize=1)
	def _create_action(self):
		actions = self._droplet_api.get_actions()
		return [a for a in actions if a.type == 'create'][0]

	def is_up(self):
		create_action = self._create_action
		create_action.load()
		return create_action.status == 'completed'
	
	@property
	@lru_cache(maxsize=1)
	def ip(self):
		self._droplet_api.load()
		return self._droplet_api.ip_address

	def all_actions(self):
		for action in self._droplet_api.get_actions():
			action.load()
			yield action

	def delete(self):
		self._droplet_api.destroy()
