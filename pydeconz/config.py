"""Python library to connect Deconz and Home Assistant to work together."""

import logging

from pprint import pprint

_LOGGER = logging.getLogger(__name__)


class DeconzConfig:
    """Deconz light representation.

    Dresden Elektroniks documentation of lights in Deconz
    http://dresden-elektronik.github.io/deconz-rest-doc/config/
    {
        'UTC': '2017-11-04T12:01:19',
        'apiversion': '1.0.4',
        'backup': {'errorcode': 0, 'status': 'idle'},
        'bridgeid': '00212EFFFF011015',
        'datastoreversion': '60',
        'dhcp': True,
        'factorynew': False,
        'gateway': '10.0.1.1',
        'internetservices': {'remoteaccess': 'disconnected'},
        'ipaddress': '10.0.1.16',
        'linkbutton': False,
        'localtime': '2017-11-04T13:01:19',
        'mac': 'b8:27:eb:2c:eb:e2',
        'modelid': 'deCONZ',
        'name': 'deCONZ-GW',
        'netmask': '255.255.255.0',
        'networkopenduration': 60,
        'panid': 50436,
        'portalconnection': 'disconnected',
        'portalservices': False,
        'portalstate': {'communication': 'disconnected',
                        'incoming': False,
                        'outgoing': False,
                        'signedon': False},
        'proxyaddress': 'none',
        'proxyport': 0,
        'replacesbridgeid': None,
        'starterkitid': '',
        'swupdate': {'checkforupdate': False,
                     'devicetypes': {'bridge': False, 'lights': [], 'sensors': []},
                     'notify': False,
                     'text': '',
                     'updatestate': 0,
                     'url': ''},
        'swversion': '2.4.82',
        'timeformat': '24h',
        'timezone': 'Europe/Stockholm',
        'uuid': '445d8b57-55ce-47ee-822f-5428e61d8073',
        'websocketnotifyall': True,
        'websocketport': 443,
        'whitelist': {'1234567890': {'create date': '2017-11-02T23:13:13',
                                     'last use date': '2017-11-04T12:00:03',
                                     'name': 'deCONZ WebApp'},},
        'wifi': 'not-installed',
        'wifiappw': '',
        'wifichannel': '1',
        'wifiip': '192.168.8.1',
        'wifiname': 'Not set',
        'wifitype': 'accesspoint',
        'zigbeechannel': 15
    }
    """

    def __init__(self, config):
    #def __init__(self, device, set_state_callback):
        """Set initial information about light.

        Set callback to set state of device.
        """
        pprint(config)
        for key, value in config.items():
            self.__setattr__("_{0}".format(key), value)
        pprint(self.__dict__)

    @property
    def apiversion(self):
        """The version of the deCONZ Rest API."""
        return self._apiversion

    @property
    def host(self):
        """IPv4 address of the gateway."""
        return self._ipaddress

    @property
    def linkbutton(self):
        """True if the gateway is unlocked."""
        return self._linkbutton

    @property
    def modelid(self):
        return self._modelid

    @property
    def name(self):
        """Name of the gateway."""
        return self._name

    @property
    def networkopenduration(self):
        """Can be used to store the permitjoin value permanently."""
        return self._networkopenduration

    @property
    def panid(self):
        """The ZigBee pan ID of the gateway."""
        return self._panid

    @property
    def swversion(self):
        """The software version of the gateway."""
        return self._swversion

    @property
    def uuid(self):
        """UPNP Unique Id of the gateway."""
        return self._uuid

    @property
    def websocketport(self):
        """Websocket port."""
        return self._websocketport

    @property
    def zigbeechannel(self):
        """The current wireless frequency channel used by the Gateway.
        
        Supported channels: 11, 15, 20, 25."""
        return self._zigbeechannel
