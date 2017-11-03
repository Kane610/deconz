"""Python library to connect Deconz and Home Assistant to work together."""

import logging

from pprint import pprint

_LOGGER = logging.getLogger(__name__)


class DeconzLight(object):
    """Deconz light representation.

    Dresden Elektroniks documentation of lights in Deconz
    http://dresden-elektronik.github.io/deconz-rest-doc/lights/
    """

    def __init__(self, light, set_state_callback):
        """Set initial information about light.

        Set callback to set state of device.
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

        self.set_state = set_state_callback
        self.callback = None

    def update_state(self, state):
        """Update state of light.

        State may contain any of the following:
        {
            "alert": "none"
            "bri": 111
            "colormode": "ct"
            "ct": 307
            "effect": "none"
            "hue": 7998
            "on": false
            "reachable": true
            "sat": 172
            "xy": [ 0.421253, 0.39921 ]
        }
        """
        if 'on' in state:
            self.state = state['on']
        if 'bri' in state:
            self.brightness = state['bri']

    def update(self, event):
        """New event for light.

        Check that state is part of event.
        Signal that light has updated state.
        """
        if 'state' in event:
            self.update_state(event['state'])
        if self.callback:
            self.callback()
        pprint(self.__dict__)

    def as_dict(self):
        """Callback for __dict__."""
        cdict = self.__dict__.copy()
        if 'set_state' in cdict:
            del cdict['set_state']
        if 'callback' in cdict:
            del cdict['callback']
        return cdict
