# coding=utf-8
from functools import lru_cache


class DropletAction:
    def __init__(self, _api_action, extra_check=None):
        self._api_action = _api_action
        self._known_to_have_finished = False
        self._extra_check = extra_check

    def is_finished(self):
        if self._known_to_have_finished:
            return True

        self._api_action.load()
        api_says_finished = self._api_action.status == 'completed'
        self._known_to_have_finished = api_says_finished and self._extra_check() if self._extra_check else True
        return self._known_to_have_finished


class Droplet(object):
    def __init__(self, _manager, _droplet_api, _machine_configuration):
        self._manager = _manager
        self._droplet_api = _droplet_api
        self._machine_configuration = _machine_configuration

    @property
    @lru_cache(maxsize=1)
    def _create_action(self):
        actions = self._droplet_api.get_actions()
        return [a for a in actions if a.type == 'create'][0]

    def is_up(self):
        create_action = self._create_action
        create_action.load()
        if create_action.status != 'completed':
            return False
        self._droplet_api.load()
        return self._droplet_api.status == 'active'

    def is_powered_down(self):
        self._droplet_api.load()
        return self._droplet_api.status == 'off'

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

    def snapshot(self):
        snapshot_name = self._manager.find_base_snapshot_name(self._machine_configuration)
        snapshot_action = self._droplet_api.take_snapshot(snapshot_name=snapshot_name, power_off=True,
                                                          return_dict=False)

        def snapshot_available():
            try:
                self._manager.find_image_id(self._machine_configuration)
                return True
            except KeyError:
                return False

        return snapshot_name, DropletAction(snapshot_action, extra_check=snapshot_available)
