"""Python library to connect deCONZ and Home Assistant to work together."""

import logging

_LOGGER = logging.getLogger(__name__)


class DeconzConfig:
    """deCONZ configuration representation.

    Dresden Elektroniks documentation of config in deCONZ
    http://dresden-elektronik.github.io/deconz-rest-doc/config/
    {
        'UTC': '2017-11-04T12:01:19',
        'apiversion': '1.0.4',
        'backup': {'errorcode': 0, 'status': 'idle'},
        'bridgeid': '0123456789ABCDEF',
        'datastoreversion': '60',
        'dhcp': True,
        'factorynew': False,
        'gateway': '192.168.0.1',
        'internetservices': {'remoteaccess': 'disconnected'},
        'ipaddress': '192.168.0.90',
        'linkbutton': False,
        'localtime': '2017-11-04T13:01:19',
        'mac': '00:11:22:33:44:55',
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
        'uuid': '12345678-90AB-CDEF-1234-1234567890AB',
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
        'zigbeechannel': 11
    }
    """

    def __init__(self, config):
        """Set initial information about light.

        Set callback to set state of device.
        """
        self._apiversion = config.get('apiversion')
        self._bridgeid = config.get('bridgeid')
        self._linkbutton = config.get('linkbutton')
        self._mac = config.get('mac')
        self._modelid = config.get('modelid')
        self._name = config.get('name')
        self._networkopenduration = config.get('networkopenduration')
        self._panid = config.get('panid')
        self._swversion = config.get('swversion')
        self._uuid = config.get('uuid')
        self._websocketport = config.get('websocketport')
        self._zigbeechannel = config.get('zigbeechannel')
        _LOGGER.debug('Deconz config loaded %s', self.__dict__)

    @property
    def apiversion(self):
        """The version of the deCONZ Rest API."""
        return self._apiversion

    @property
    def bridgeid(self):
        """Hardware ID."""
        return self._bridgeid

    @property
    def linkbutton(self):
        """True if the gateway is unlocked."""
        return self._linkbutton

    @property
    def mac(self):
        """MAC address of the gateway"""
        return self._mac

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
