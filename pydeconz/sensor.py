import logging

from pprint import pprint

_LOGGER = logging.getLogger(__name__)

# Wireless dimmer
# 1002 Move to level 255
# 2002 Move up
# 3002 Move down
# 4002 Move to level 0


class DeconzSensor:
    """
    """
    def __init__(self, sensor):
        """
        """
        self.state = None
        self.name = sensor['name']
        self.type = sensor['type']
        self.modelid = sensor['modelid']
        self.swversion = sensor['swversion']
        self.uniqueid = sensor['uniqueid']
        self.manufacturer = sensor['manufacturername']

        self.battery = sensor['config']['battery']
        self.reachable = sensor['config']['reachable']

        self.callback = None
    
    def update_config(self, config):
        """
        """
        self.battery = config['battery']
        self.reachable = config['reachable']
    
    def update_state(self, state):
        """
        """
        raise NotImplementedError

    def update(self, event):
        """
        """
        if 'state' in event:
            self.update_state(event['state'])
        if 'config' in event:
            self.update_config(event['config'])
        if self.callback:
            self.callback()
        pprint(self.__dict__)

    def as_dict(self):
        """Callback for __dict__.
        """
        cdict = self.__dict__.copy()
        if 'callback' in cdict:
            del cdict['callback']
        return cdict


class ZHAPresence(DeconzSensor):
    """
    """
    def __init__(self, sensor):
        """
        """
        super().__init__(sensor)
        self.state = False
        self.dark = sensor.get('dark')

    def update_state(self, state):
        """
        """
        self.state = state['presence']
        self.dark = state.get('dark')

    @property
    def is_tripped(self):
        """Event is tripped now.
        """
        return self.state


class ZHASwitch(DeconzSensor):
    """
    """
    def __init__(self, sensor):
        """
        """
        super().__init__(sensor)
        self.state = None

    def update_state(self, state):
        """
        """
        self.state = state['buttonevent']
