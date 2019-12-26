"""Python library to connect deCONZ and Home Assistant to work together."""

import logging

from .utils import normalize_bridge_id

_LOGGER = logging.getLogger(__name__)


class DeconzConfig:
    """deCONZ configuration representation.

    Dresden Elektroniks documentation of config in deCONZ
    http://dresden-elektronik.github.io/deconz-rest-doc/config/
    """

    def __init__(self, raw):
        """Set configuration about deCONZ gateway."""
        self.raw = raw

    @property
    def apiversion(self):
        """deCONZ Rest API version."""
        return self.raw.get("apiversion")

    @property
    def bridgeid(self):
        """Hardware ID."""
        return normalize_bridge_id(self.raw.get("bridgeid"))

    @property
    def linkbutton(self):
        """True if gateway is unlocked."""
        return self.raw.get("linkbutton")

    @property
    def mac(self):
        """MAC address of gateway."""
        return self.raw.get("mac")

    @property
    def modelid(self):
        """Model describing either conbee or raspbee."""
        return self.raw.get("modelid")

    @property
    def name(self):
        """Name of the gateway."""
        return self.raw.get("name")

    @property
    def networkopenduration(self):
        """Can be used to store the permitjoin value permanently."""
        return self.raw.get("networkopenduration")

    @property
    def panid(self):
        """The ZigBee pan ID of the gateway."""
        return self.raw.get("panid")

    @property
    def swversion(self):
        """The software version of the gateway."""
        return self.raw.get("swversion")

    @property
    def uuid(self):
        """UPNP Unique Id of the gateway."""
        return self.raw.get("uuid")

    @property
    def websocketport(self):
        """Websocket port."""
        return self.raw.get("websocketport")

    @property
    def zigbeechannel(self):
        """The current wireless frequency channel used by the Gateway.

        Supported channels: 11, 15, 20, 25."""
        return self.raw.get("zigbeechannel")
