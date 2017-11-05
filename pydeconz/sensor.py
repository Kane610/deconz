"""Python library to connect Deconz and Home Assistant to work together."""

import logging

from pprint import pprint

from .deconzdevice import DeconzDevice

_LOGGER = logging.getLogger(__name__)

# Wireless dimmer
# 1002 Move to level 255
# 2002 Move up
# 3002 Move down
# 4002 Move to level 0


class DeconzSensor(DeconzDevice):
    """Deconz sensor representation.

    Dresden Elektroniks documentation of sensors in Deconz
    http://dresden-elektronik.github.io/deconz-rest-doc/sensors/
    """

    def __init__(self, device):
        """Set initial information about sensor.

        Set callback to set state of device.
        """
        self._battery = device['config'].get('battery')
        self._ep = device.get('ep')
        self._on = device['config'].get('on')
        self._reachable = device['config'].get('reachable')
        super().__init__(device)

    def update(self, event):
        """New event for sensor.

        Check if state is part of event.
        Check if config is part of event.
        Signal that sensor has updated state.
        """
        for data in ['state', 'config']:
            self.update_attr(event.get(data, {}))
        super().update(event)

    @property
    def battery(self):
        """The battery status of the sensor."""
        return self._battery

    @property
    def ep(self):
        """The Endpoint of the sensor."""
        return self._ep

    @property
    def on(self):
        """Specifies if the sensor is on or off."""
        return self._on

    @property
    def reachable(self):
        """Specifies if the sensor is reachable."""
        return self._reachable


class ZHAPresence(DeconzSensor):
    """Presence detector."""

    def __init__(self, device):
        """Initialize presence detector."""
        self._dark = device['state'].get('dark')
        self._presence = device['state'].get('presence')
        super().__init__(device)

    @property
    def is_tripped(self):
        """Sensor is tripped."""
        return self.presence

    @property
    def dark(self):
        """If the area near the sensor as light or not."""
        return self._dark

    @property
    def presence(self):
        """Motion detected."""
        return self._presence


class ZHASwitch(DeconzSensor):
    """Switch."""

    def __init__(self, device):
        """Initalize switch."""
        self._buttonevent = device['state'].get('buttonevent')
        super().__init__(device)

    @property
    def state(self):
        """Main state of switch."""
        return self.buttonevent

    @property
    def buttonevent(self):
        """Button press"""
        return self._buttonevent
