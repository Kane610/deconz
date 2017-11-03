import logging

from pprint import pprint

_LOGGER = logging.getLogger(__name__)


class DeconzLight(object):
    """
    """
    def __init__(self, light, set_state):
        """
        """
        print(light)
        self.state = light['state']['on']
        self.name = light['name']
        self.type = light['type']
        self.modelid = light['modelid']
        self.swversion = light['swversion']
        self.uniqueid = light['uniqueid']
        self.manufacturer = light['manufacturername']

        self.hascolor = light['hascolor']
        self.brightness = light['state']['bri']
        self.reachable = light['state']['reachable']

        self.set_state = set_state
        self.callback = None

    def update_state(self, state):
        """
        """
        if 'on' in state:
            self.state = state['on']
        if 'bri' in state:
            self.brightness = state['bri']

    def update(self, event):
        """
        """
        if 'state' in event:
            self.update_state(event['state'])
        if self.callback:
            self.callback()
        pprint(self.__dict__)

    def as_dict(self):
        """Callback for __dict__.
        """
        cdict = self.__dict__.copy()
        if 'set_state' in cdict:
            del cdict['set_state']
        if 'callback' in cdict:
            del cdict['callback']
        return cdict
