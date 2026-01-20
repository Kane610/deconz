"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from typing import Any, Final, Literal, TypedDict

from ..utils import normalize_bridge_id
from .api import APIItem

UNINITIALIZED_BRIDGE_ID: Final = "0000000000000000"


class TypedConfig(TypedDict):
    """Config type definition."""

    apiversion: str
    backup: dict[str, Any]
    bridgeid: str
    datastoreversion: str
    devicename: str
    dhcp: bool
    factorynew: bool
    fwversion: str
    gateway: str
    internetservices: dict[str, Any]
    ipaddress: str
    lightlastseeninterval: int
    linkbutton: bool
    localtime: str
    mac: str
    modelid: str
    name: str
    netmask: str
    networkopenduration: int
    ntp: Literal["synced", "unsynced"]
    panid: int
    portalservices: bool
    portalstate: dict[str, Any]
    proxyaddress: str
    proxyport: int
    replacesbridgeid: str
    rfconnected: bool
    starterkitid: str
    swupdate: dict[str, Any]
    swupdate2: dict[str, Any]
    swversion: str
    timeformat: Literal["12h", "24h"]
    timezone: str
    UTC: str
    uuid: str
    websocketnotifyall: bool
    websocketport: int
    whitelist: dict[str, dict[str, str]]
    zigbeechannel: int


class Config(APIItem):
    """Config class."""

    raw: TypedConfig

    @property
    def api_version(self) -> str | None:
        """Version of the deCONZ Rest API."""
        return self.raw.get("apiversion")

    @property
    def bridge_id(self) -> str:
        """Gateway unique identifier."""
        return normalize_bridge_id(self.raw.get("bridgeid", UNINITIALIZED_BRIDGE_ID))

    @property
    def device_name(self) -> str | None:
        """Product name of the gateway.

        Valid values are "ConBee", "RaspBee", "ConBee II" and "RaspBee II".
        """
        return self.raw.get("devicename")

    @property
    def dhcp(self) -> bool | None:
        """Whether the IP address of the bridge is obtained with DHCP."""
        return self.raw.get("dhcp")

    @property
    def firmware_version(self) -> str | None:
        """Version of the ZigBee firmware."""
        return self.raw.get("fwversion")

    @property
    def gateway(self) -> str | None:
        """IPv4 address of the gateway."""
        return self.raw.get("gateway")

    @property
    def ip_address(self) -> str | None:
        """IPv4 address of the gateway."""
        return self.raw.get("ipaddress")

    @property
    def link_button(self) -> bool | None:
        """Is gateway unlocked."""
        return self.raw.get("linkbutton")

    @property
    def local_time(self) -> str | None:
        """Localtime of the gateway."""
        return self.raw.get("localtime")

    @property
    def mac(self) -> str | None:
        """MAC address of gateway."""
        return self.raw.get("mac")

    @property
    def model_id(self) -> str | None:
        """Model describing either conbee or raspbee."""
        return self.raw.get("modelid")

    @property
    def name(self) -> str | None:
        """Name of the gateway."""
        return self.raw.get("name")

    @property
    def network_mask(self) -> str | None:
        """Network mask of the gateway."""
        return self.raw.get("netmask")

    @property
    def network_open_duration(self) -> int | None:
        """Duration in seconds used by lights and sensors search."""
        return self.raw.get("networkopenduration")

    @property
    def ntp(self) -> Literal["synced", "unsynced"] | None:
        """Tells if the NTP time is "synced" or "unsynced".

        Only for gateways running on Linux.
        """
        return self.raw.get("ntp")

    @property
    def pan_id(self) -> int | None:
        """Zigbee pan ID of the gateway."""
        return self.raw.get("panid")

    @property
    def portal_services(self) -> bool | None:
        """State of registration to portal service.

        Is the bridge registered to synchronize data with a portal account.
        """
        return self.raw.get("portalservices")

    @property
    def rf_connected(self) -> bool | None:
        """State of deCONZ connection to firmware and if Zigbee network is up."""
        return self.raw.get("rfconnected")

    @property
    def software_update(self) -> dict[str, Any]:
        """Contains information related to software updates."""
        return self.raw.get("swupdate", {})

    @property
    def software_version(self) -> str | None:
        """Software version of the gateway."""
        return self.raw.get("swversion")

    @property
    def time_format(self) -> Literal["12h", "24h"] | None:
        """Timeformat used by gateway.

        Supported values:
        "12h" or "24h"
        """
        return self.raw.get("timeformat")

    @property
    def time_zone(self) -> str | None:
        """Time zone used by gateway.

        Only on Raspberry Pi.
        "None" if not further specified.
        """
        return self.raw.get("timezone")

    @property
    def utc(self) -> str | None:
        """UTC time of gateway in ISO 8601 format."""
        return self.raw.get("UTC")

    @property
    def uuid(self) -> str | None:
        """UPNP Unique ID of the gateway."""
        return self.raw.get("uuid")

    @property
    def websocket_notify_all(self) -> bool | None:
        """All state changes will be signalled through the Websocket connection.

        Default true.
        """
        return self.raw.get("websocketnotifyall")

    @property
    def websocket_port(self) -> int | None:
        """Websocket port."""
        return self.raw.get("websocketport")

    @property
    def whitelist(self) -> dict[str, Any]:
        """Array of whitelisted API keys."""
        return self.raw.get("whitelist", {})
