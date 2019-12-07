"""Test pydeCONZ config.

pytest --cov-report term-missing --cov=pydeconz.config tests/test_config.py
"""

from pydeconz.config import DeconzConfig


async def test_create_config():
    """Verify that creating a config works."""
    config = DeconzConfig(FIXTURE_CONFIG)

    assert config.apiversion == "1.0.4"
    assert config.bridgeid == "0123456789ABCDEF"
    assert config.linkbutton is False
    assert config.mac == "00:11:22:33:44:55"
    assert config.modelid == "deCONZ"
    assert config.name == "deCONZ-GW"
    assert config.networkopenduration == 60
    assert config.panid == 50436
    assert config.swversion == "2.4.82"
    assert config.uuid == "12345678-90AB-CDEF-1234-1234567890AB"
    assert config.websocketport == 443
    assert config.zigbeechannel == 11


FIXTURE_CONFIG = {
    "UTC": "2017-11-04T12:01:19",
    "apiversion": "1.0.4",
    "backup": {"errorcode": 0, "status": "idle"},
    "bridgeid": "0123456789ABCDEF",
    "datastoreversion": "60",
    "dhcp": True,
    "factorynew": False,
    "gateway": "192.168.0.1",
    "internetservices": {"remoteaccess": "disconnected"},
    "ipaddress": "192.168.0.90",
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
