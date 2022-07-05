"""Test pydeCONZ config.

pytest --cov-report term-missing --cov=pydeconz.config tests/test_config.py
"""

from pydeconz.config import (
    ConfigDeviceName,
    ConfigNTP,
    ConfigTimeFormat,
    ConfigUpdateChannel,
    ConfigZigbeeChannel,
)


async def test_create_config(
    mock_aioresponse, deconz_refresh_state, deconz_called_with
):
    """Verify that creating a config works."""
    deconz_session = await deconz_refresh_state(config=FIXTURE_CONFIG)
    config = deconz_session.config

    assert config.api_version == "1.0.4"
    assert config.bridge_id == "0123456789AB"
    assert config.device_name == ConfigDeviceName.UNKNOWN
    assert config.dhcp
    assert config.firmware_version == "0x26490700"
    assert config.gateway == "192.168.0.1"
    assert config.ip_address == "192.168.0.90"
    assert config.link_button is False
    assert config.local_time == "2017-11-04T13:01:19"
    assert config.mac == "00:11:22:33:44:55"
    assert config.model_id == "deCONZ"
    assert config.name == "deCONZ-GW"
    assert config.network_mask == "255.255.255.0"
    assert config.network_open_duration == 60
    assert not config.ntp
    assert config.pan_id == 50436
    assert not config.portal_services
    assert config.rf_connected
    assert config.software_update == {
        "checkforupdate": False,
        "devicetypes": {"bridge": False, "lights": [], "sensors": []},
        "notify": False,
        "text": "",
        "updatestate": 0,
        "url": "",
    }
    assert config.software_version == "2.4.82"
    assert config.time_format == ConfigTimeFormat.FORMAT_24H
    assert config.time_zone == "Europe/Stockholm"
    assert not config.utc
    assert config.uuid == "12345678-90AB-CDEF-1234-1234567890AB"
    assert config.websocket_notify_all
    assert config.websocket_port == 443
    assert config.whitelist == {
        "1234567890": {
            "create date": "2017-11-02T23:13:13",
            "last use date": "2017-11-04T12:00:03",
            "name": "deCONZ WebApp",
        }
    }
    assert config.zigbee_channel == ConfigZigbeeChannel.CHANNEL_11

    del config.raw["bridgeid"]
    assert config.bridge_id == "0000000000000000"

    config.raw["bridgeid"] = "00212EFFFF012345"
    assert config.bridge_id == "00212E012345"

    config.raw["ntp"] = "synced"
    assert config.ntp == ConfigNTP.SYNCED

    mock_aioresponse.put("http://host:80/api/apikey/config")
    await config.set_config(
        discovery=True,
        group_delay=1000,
        light_last_seen_interval=100,
        name="ABC",
        network_open_duration=10,
        otau_active=False,
        permit_join=111,
        rf_connected=True,
        time_format=ConfigTimeFormat.FORMAT_24H,
        time_zone="Europe/Stockholm",
        unlock=200,
        update_channel=ConfigUpdateChannel.BETA,
        utc="2017-11-04T12:01:19",
        zigbee_channel=ConfigZigbeeChannel.CHANNEL_15,
        websocket_notify_all=False,
    )
    assert deconz_called_with(
        "put",
        path="/config",
        json={
            "discovery": True,
            "groupdelay": 1000,
            "lightlastseeninterval": 100,
            "name": "ABC",
            "networkopenduration": 10,
            "otauactive": False,
            "permitjoin": 111,
            "rfconnected": True,
            "timeformat": "24h",
            "timezone": "Europe/Stockholm",
            "unlock": 200,
            "updatechannel": "beta",
            "utc": "2017-11-04T12:01:19",
            "zigbeechannel": 15,
            "websocketnotifyall": False,
        },
    )


FIXTURE_CONFIG = {
    "UTC": "2017-11-04T12:01:19",
    "apiversion": "1.0.4",
    "backup": {"errorcode": 0, "status": "idle"},
    "bridgeid": "0123456789AB",
    "datastoreversion": "60",
    "devicename": "",
    "dhcp": True,
    "disablePermitJoinAutoOff": False,
    "factorynew": False,
    "fwversion": "0x26490700",
    "gateway": "192.168.0.1",
    "internetservices": {"remoteaccess": "disconnected"},
    "ipaddress": "192.168.0.90",
    "lightlastseeninterval": 60,
    "linkbutton": False,
    "localtime": "2017-11-04T13:01:19",
    "mac": "00:11:22:33:44:55",
    "modelid": "deCONZ",
    "name": "deCONZ-GW",
    "netmask": "255.255.255.0",
    "networkopenduration": 60,
    "panid": 50436,
    "portalconnection": "disconnected",
    "portalservices": False,
    "portalstate": {
        "communication": "disconnected",
        "incoming": False,
        "outgoing": False,
        "signedon": False,
    },
    "proxyaddress": "none",
    "proxyport": 0,
    "replacesbridgeid": None,
    "rfconnected": True,
    "starterkitid": "",
    "swupdate": {
        "checkforupdate": False,
        "devicetypes": {"bridge": False, "lights": [], "sensors": []},
        "notify": False,
        "text": "",
        "updatestate": 0,
        "url": "",
    },
    "swversion": "2.4.82",
    "timeformat": "24h",
    "timezone": "Europe/Stockholm",
    "uuid": "12345678-90AB-CDEF-1234-1234567890AB",
    "websocketnotifyall": True,
    "websocketport": 443,
    "whitelist": {
        "1234567890": {
            "create date": "2017-11-02T23:13:13",
            "last use date": "2017-11-04T12:00:03",
            "name": "deCONZ WebApp",
        }
    },
    "wifi": "not-installed",
    "wifiappw": "",
    "wifichannel": "1",
    "wifiip": "192.168.8.1",
    "wifiname": "Not set",
    "wifitype": "accesspoint",
    "zigbeechannel": 11,
}
