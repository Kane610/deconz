"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
import enum
import logging
from typing import Any, Final

from .utils import normalize_bridge_id

LOGGER = logging.getLogger(__name__)


UNINITIALIZED_BRIDGE_ID: Final = "0000000000000000"


class ConfigDeviceName(enum.Enum):
    """Valid product names of the gateway."""

    CONBEE = "ConBee"
    RASPBEE = "RaspBee"
    CONBEE_2 = "ConBee II"
    RASPBEE_2 = "RaspBee II"

    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls, value: object) -> "ConfigDeviceName":
        """Set default enum member if an unknown value is provided."""
        LOGGER.warning("Unexpected config device name %s", value)
        return ConfigDeviceName.UNKNOWN


class ConfigNTP(enum.Enum):
    """Timeformat that can be used by other applications."""

    SYNCED = "synced"
    UNSYNCED = "unsynced"


class ConfigTimeFormat(enum.Enum):
    """Tells if the NTP time is "synced" or "unsynced"."""

    FORMAT_12H = "12h"
    FORMAT_24H = "24h"


class ConfigUpdateChannel(enum.Enum):
    """Available update channels to use with the Gateway."""

    ALPHA = "alpha"
    BETA = "beta"
    STABLE = "stable"


class ConfigZigbeeChannel(enum.IntEnum):
    """Available wireless frequency channels to use with the Gateway."""

    CHANNEL_11 = 11
    CHANNEL_15 = 15
    CHANNEL_20 = 20
    CHANNEL_25 = 25


class Config:
    """deCONZ configuration representation.

    Dresden Elektroniks documentation of config in deCONZ
    http://dresden-elektronik.github.io/deconz-rest-doc/config/
    """

    def __init__(
        self,
        raw: dict[str, Any],
        request: Callable[..., Awaitable[dict[str, Any]]],
    ) -> None:
        """Set configuration about deCONZ gateway."""
        self.raw = raw
        self.request = request

    @property
    def api_version(self) -> str | None:
        """Version of the deCONZ Rest API."""
        return self.raw.get("apiversion")

    @property
    def bridge_id(self) -> str:
        """Gateway unique identifier."""
        return normalize_bridge_id(self.raw.get("bridgeid", UNINITIALIZED_BRIDGE_ID))

    @property
    def device_name(self) -> ConfigDeviceName:
        """Product name of the gateway.

        Valid values are "ConBee", "RaspBee", "ConBee II" and "RaspBee II".
        """
        return ConfigDeviceName(self.raw.get("devicename"))

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
        """Model identifyer.

        Fixed string "deCONZ".
        """
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
    def ntp(self) -> ConfigNTP | None:
        """Tells if the NTP time is "synced" or "unsynced".

        Only for gateways running on Linux.
        """
        if "ntp" in self.raw:
            return ConfigNTP(self.raw["ntp"])
        return None

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
    def software_update(self) -> dict[str, Any] | None:
        """Contains information related to software updates."""
        return self.raw.get("swupdate")

    @property
    def software_version(self) -> str | None:
        """Software version of the gateway."""
        return self.raw.get("swversion")

    @property
    def time_format(self) -> ConfigTimeFormat:
        """Timeformat used by gateway.

        Supported values:
        "12h" or "24h"
        """
        return ConfigTimeFormat(self.raw["timeformat"])

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
        return self.raw.get("utc")

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

    @property
    def zigbee_channel(self) -> ConfigZigbeeChannel:
        """Wireless frequency channel."""
        return ConfigZigbeeChannel(self.raw["zigbeechannel"])

    async def set_config(
        self,
        discovery: bool | None = None,
        group_delay: int | None = None,
        light_last_seen_interval: int | None = None,
        name: str | None = None,
        network_open_duration: int | None = None,
        otau_active: bool | None = None,
        permit_join: int | None = None,
        rf_connected: bool | None = None,
        time_format: ConfigTimeFormat | None = None,
        time_zone: str | None = None,
        unlock: int | None = None,
        update_channel: ConfigUpdateChannel | None = None,
        utc: str | None = None,
        zigbee_channel: ConfigZigbeeChannel | None = None,
        websocket_notify_all: bool | None = None,
    ) -> dict[str, Any]:
        """Modify configuration parameters.

        Supported values:
        - discovery [bool]
            Set gateway discovery over the internet active or inactive.
        - group_delay [int] 0-5000
            Time between two group commands in milliseconds.
        - light_last_seen_interval [int] 1-65535 default 60
            Sets the number of seconds where the timestamp for "lastseen"
            is updated at the earliest for light resources. For any such update,
            a seperate websocket event will be triggered.
        - name [str] 0-16 characters
            Name of the gateway.
        - network_open_duration [int] 1-65535
            Sets the lights and sensors search duration in seconds.
        - otau_active [bool]
            Set OTAU active or inactive
        - permit_join [int] 0-255
            Open the network so that other zigbee devices can join.
            0 = network closed
            255 = network open
            1–254 = time in seconds the network remains open
            The value will decrement automatically.
        - rf_connected [bool]
            Set to true to bring the Zigbee network up and false to bring it down.
            This has the same effect as using the Join and Leave buttons in deCONZ.
        - time_format [str] 12h|24h
            Can be used to store the timeformat permanently.
        - time_zone [str]
            Set the timezone of the gateway (only on Raspberry Pi).
        - unlock [int] 0-600 (seconds)
            Unlock the gateway so that apps can register themselves to the gateway.
        - update_channel [str] stable|alpha|beta
            Set update channel.
        - utc [str]
            Set the UTC time of the gateway (only on Raspbery Pi)
            in ISO 8601 format (yyyy-MM-ddTHH:mm:ss).
        - zigbee_channel [int] 11|15|20|25
            Set the zigbeechannel of the gateway.
            Notify other Zigbee devices also to change their channel.
        - websocket_notify_all [bool] default True
            When true all state changes will be signalled through the websocket connection.
        """
        data = {
            key: value
            for key, value in {
                "discovery": discovery,
                "groupdelay": group_delay,
                "lightlastseeninterval": light_last_seen_interval,
                "name": name,
                "networkopenduration": network_open_duration,
                "otauactive": otau_active,
                "permitjoin": permit_join,
                "rfconnected": rf_connected,
                "timezone": time_zone,
                "unlock": unlock,
                "utc": utc,
                "websocketnotifyall": websocket_notify_all,
            }.items()
            if value is not None
        }
        if time_format is not None:
            data["timeformat"] = time_format.value
        if update_channel is not None:
            data["updatechannel"] = update_channel.value
        if zigbee_channel is not None:
            data["zigbeechannel"] = zigbee_channel.value
        return await self.request("put", path="/config", json=data)
