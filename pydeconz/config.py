"""Python library to connect deCONZ and Home Assistant to work together."""

from typing import Any, Awaitable, Callable, Dict, Final, Literal, Optional

from .utils import normalize_bridge_id

RESOURCE_TYPE: Final = "config"

UNINITIALIZED_BRIDGE_ID: Final = "0000000000000000"


class Config:
    """deCONZ configuration representation.

    Dresden Elektroniks documentation of config in deCONZ
    http://dresden-elektronik.github.io/deconz-rest-doc/config/
    """

    def __init__(
        self,
        raw: dict,
        request: Callable[..., Awaitable[Dict[str, Any]]],
    ) -> None:
        """Set configuration about deCONZ gateway."""
        self.raw = raw
        self.request = request

    @property
    def api_version(self) -> Optional[str]:
        """Version of the deCONZ Rest API."""
        return self.raw.get("apiversion")

    @property
    def bridge_id(self) -> str:
        """Gateway unique identifier."""
        return normalize_bridge_id(self.raw.get("bridgeid", UNINITIALIZED_BRIDGE_ID))

    @property
    def device_name(self) -> Optional[str]:
        """Product name of the gateway.

        Valid values are "ConBee", "RaspBee", "ConBee II" and "RaspBee II".
        """
        return self.raw.get("devicename")

    @property
    def dhcp(self) -> Optional[bool]:
        """Whether the IP address of the bridge is obtained with DHCP."""
        return self.raw.get("dhcp")

    @property
    def firmware_version(self) -> Optional[str]:
        """Version of the ZigBee firmware."""
        return self.raw.get("fwversion")

    @property
    def gateway(self) -> Optional[str]:
        """IPv4 address of the gateway."""
        return self.raw.get("gateway")

    @property
    def ip_address(self) -> Optional[str]:
        """IPv4 address of the gateway."""
        return self.raw.get("ipaddress")

    @property
    def link_button(self) -> Optional[bool]:
        """Is gateway unlocked."""
        return self.raw.get("linkbutton")

    @property
    def local_time(self) -> Optional[bool]:
        """Localtime of the gateway."""
        return self.raw.get("localtime")

    @property
    def mac(self) -> Optional[str]:
        """MAC address of gateway."""
        return self.raw.get("mac")

    @property
    def model_id(self) -> Optional[str]:
        """Model describing either conbee or raspbee."""
        return self.raw.get("modelid")

    @property
    def name(self) -> Optional[str]:
        """Name of the gateway."""
        return self.raw.get("name")

    @property
    def network_mask(self) -> Optional[str]:
        """Network mask of the gateway."""
        return self.raw.get("netmask")

    @property
    def network_open_duration(self) -> Optional[int]:
        """Duration in seconds used by lights and sensors search."""
        return self.raw.get("networkopenduration")

    @property
    def ntp(self) -> Literal["synced", "unsynced", None]:
        """Tells if the NTP time is "synced" or "unsynced".

        Only for gateways running on Linux.
        """
        return self.raw.get("ntp")

    @property
    def pan_id(self) -> Optional[int]:
        """Zigbee pan ID of the gateway."""
        return self.raw.get("panid")

    @property
    def portal_services(self) -> Optional[bool]:
        """State of registration to portal service.

        Is the bridge registered to synchronize data with a portal account.
        """
        return self.raw.get("portalservices")

    @property
    def rf_connected(self) -> Optional[bool]:
        """State of deCONZ connection to firmware and if Zigbee network is up."""
        return self.raw.get("rfconnected")

    @property
    def software_update(self) -> Optional[dict]:
        """Contains information related to software updates."""
        return self.raw.get("swupdate")

    @property
    def software_version(self) -> Optional[str]:
        """Software version of the gateway."""
        return self.raw.get("swversion")

    @property
    def time_format(self) -> Literal["12h", "24h", None]:
        """Timeformat used by gateway.

        Supported values:
        "12h" or "24h"
        """
        return self.raw.get("timeformat")

    @property
    def time_zone(self) -> Optional[str]:
        """Time zone used by gateway.

        Only on Raspberry Pi.
        "None" if not further specified.
        """
        return self.raw.get("timezone")

    @property
    def utc(self) -> Optional[str]:
        """UTC time of gateway in ISO 8601 format."""
        return self.raw.get("utc")

    @property
    def uuid(self) -> Optional[str]:
        """UPNP Unique ID of the gateway."""
        return self.raw.get("uuid")

    @property
    def websocket_notify_all(self) -> Optional[bool]:
        """All state changes will be signalled through the Websocket connection.

        Default true.
        """
        return self.raw.get("websocketnotifyall")

    @property
    def websocket_port(self) -> Optional[int]:
        """Websocket port."""
        return self.raw.get("websocketport")

    @property
    def whitelist(self) -> Optional[dict]:
        """Array of whitelisted API keys."""
        return self.raw.get("whitelist")

    @property
    def zigbee_channel(self) -> Literal[11, 15, 20, 25, None]:
        """Wireless frequency channel.

        Supported channels: 11, 15, 20, 25.
        """
        return self.raw.get("zigbeechannel")

    async def set_config(
        self,
        discovery: Optional[bool] = None,
        group_delay: Optional[int] = None,
        light_last_seen_interval: Optional[int] = None,
        name: Optional[str] = None,
        network_open_duration: Optional[int] = None,
        otau_active: Optional[bool] = None,
        permit_join: Optional[int] = None,
        rf_connected: Optional[bool] = None,
        time_format: Literal["12h", "24h", None] = None,
        time_zone: Optional[str] = None,
        unlock: Optional[int] = None,
        update_channel: Literal["alpha", "beta", "stable", None] = None,
        utc: Optional[str] = None,
        zigbee_channel: Literal[11, 15, 20, 25, None] = None,
        websocket_notify_all: Optional[bool] = None,
    ) -> Dict[str, Any]:
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
                "timeformat": time_format,
                "timezone": time_zone,
                "unlock": unlock,
                "updatechannel": update_channel,
                "utc": utc,
                "zigbeechannel": zigbee_channel,
                "websocketnotifyall": websocket_notify_all,
            }.items()
            if value is not None
        }
        return await self.request("put", path="/config", json=data)
