"""Python library to connect deCONZ and Home Assistant to work together."""

import logging
from typing import Optional

from .utils import normalize_bridge_id

_LOGGER = logging.getLogger(__name__)

UNINITIALIZED_BRIDGE_ID = "0000000000000000"


class DeconzConfig:
    """deCONZ configuration representation.

    Dresden Elektroniks documentation of config in deCONZ
    http://dresden-elektronik.github.io/deconz-rest-doc/config/
    """

    def __init__(self, raw: dict) -> None:
        """Set configuration about deCONZ gateway."""
        self.raw = raw

    @property
    def apiversion(self) -> Optional[str]:
        """Rest API version."""
        return self.raw.get("apiversion")

    @property
    def bridgeid(self) -> str:
        """Hardware ID."""
        return normalize_bridge_id(self.raw.get("bridgeid", UNINITIALIZED_BRIDGE_ID))

    @property
    def linkbutton(self) -> Optional[bool]:
        """Is gateway unlocked."""
        return self.raw.get("linkbutton")

    @property
    def mac(self) -> Optional[str]:
        """MAC address of gateway."""
        return self.raw.get("mac")

    @property
    def modelid(self) -> Optional[str]:
        """Model describing either conbee or raspbee."""
        return self.raw.get("modelid")

    @property
    def name(self) -> Optional[str]:
        """Name of the gateway."""
        return self.raw.get("name")

    @property
    def networkopenduration(self) -> Optional[int]:
        """Can be used to store the permitjoin value permanently."""
        return self.raw.get("networkopenduration")

    @property
    def panid(self) -> Optional[int]:
        """Zigbee pan ID."""
        return self.raw.get("panid")

    @property
    def swversion(self) -> Optional[str]:
        """Software version."""
        return self.raw.get("swversion")

    @property
    def uuid(self) -> Optional[str]:
        """UPNP Unique Id of the gateway."""
        return self.raw.get("uuid")

    @property
    def websocketport(self) -> Optional[int]:
        """Websocket port."""
        return self.raw.get("websocketport")

    @property
    def zigbeechannel(self) -> Optional[int]:
        """Wireless frequency channel.

        Supported channels: 11, 15, 20, 25.
        """
        return self.raw.get("zigbeechannel")
