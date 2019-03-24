"""Python library to connect deCONZ and Home Assistant to work together."""

import logging

from .light import DeconzLightBase

_LOGGER = logging.getLogger(__name__)


class DeconzGroup(DeconzLightBase):
    """deCONZ light group representation.

    Dresden Elektroniks documentation of light groups in deCONZ
    http://dresden-elektronik.github.io/deconz-rest-doc/groups/
    """

    def __init__(self, device_id, device, async_set_state_callback):
        """Set initial information about light group.

        Set callback to set state of device.
        """
        deconz_id = '/groups/' + device_id
        self._all_on = device['state'].get('all_on')
        self._any_on = device['state'].get('any_on')
        self._bri = device['action'].get('bri')
        self._class = device.get('class')
        self._colormode = device['action'].get('colormode')
        self._ct = device['action'].get('ct')
        self._devicemembership = device.get('devicemembership')
        self._effect = device['action'].get('effect')
        self._hidden = device.get('hidden')
        self._hue = device['action'].get('hue')
        self._id = device.get('id')
        self._lights = device.get('lights')
        self._lightsequence = device.get('lightsequence')
        self._multideviceids = device.get('multideviceids')
        self._on = device['action'].get('on')
        self._reachable = True
        self._sat = device['action'].get('sat')
        self._scenes = {}
        self._xy = (None, None)
        self._x, self._y = device['action'].get('xy', (None, None))
        super().__init__(deconz_id, device, async_set_state_callback)
        self.async_add_scenes(device.get('scenes'), async_set_state_callback)

    async def async_set_state(self, data):
        """Set state of light group.

        {
            "on": true,
            "bri": 180,
            "hue": 43680,
            "sat": 255,
            "transitiontime": 10
        }

        Also update local values of group since websockets doesn't.
        """
        field = self.deconz_id + '/action'
        await self._async_set_state_callback(field, data)
        self.async_update({'state': data})

    def as_dict(self):
        """Callback for __dict__."""
        cdict = super().as_dict()
        if '_scenes' in cdict:
            del cdict['_scenes']
        return cdict

    @property
    def state(self):
        """True if any light in light group is on."""
        return self._any_on

    @property
    def groupclass(self):
        """"""
        return self._class

    @property
    def all_on(self):
        """True if all lights in light group are on"""
        return self._all_on

    @property
    def devicemembership(self):
        """List of device ids (sensors) when group was created by a device."""
        return self._devicemembership

    @property
    def hidden(self):
        """Indicate the hidden status of the group.

        Has no effect at the gateway but apps can uses this to hide groups.
        """
        return self._hidden

    @property
    def id(self):
        """The id of the group."""
        return self._id

    @property
    def lights(self):
        """A list of all light ids of this group.

        Sequence is defined by the gateway.
        """
        return self._lights

    @property
    def lightsequence(self):
        """A list of light ids of this group that can be sorted by the user.

        Need not to contain all light ids of this group.
        """
        return self._lightsequence

    @property
    def multideviceids(self):
        """A list of light ids of this group.

        Subsequent ids from multidevices with multiple endpoints.
        """
        return self._multideviceids

    @property
    def scenes(self):
        """A list of scenes of the group."""
        return self._scenes

    def async_add_scenes(self, scenes, async_set_state_callback):
        """Add scenes belonging to group."""
        self._scenes = {
            scene['id']: DeconzScene(self, scene, async_set_state_callback)
            for scene in scenes
            if scene['id'] not in self._scenes
        }

    def update_color_state(self, light):
        """Sync color state with light."""
        x, y = light.xy or (None, None)
        self.async_update({
            'state': {
                'bri': light.brightness,
                'hue': light.hue,
                'sat': light.sat,
                'ct': light.ct,
                'x': x,
                'y': y,
                'colormode': light.colormode,
            },
        })


class DeconzScene:
    """deCONZ scene representation.

    Dresden Elektroniks documentation of scenes in deCONZ
    http://dresden-elektronik.github.io/deconz-rest-doc/scenes/
    """

    def __init__(self, group, scene, async_set_state_callback):
        """Set initial information about scene.

        Set callback to set state of device.
        """
        self._group_id = group.id
        self._group_name = group.name
        self._id = scene.get('id')
        self._name = scene.get('name')
        self._deconz_id = group.deconz_id + '/scenes/' + self._id
        self._async_set_state_callback = async_set_state_callback

    async def async_set_state(self, data):
        """Recall scene to group."""
        field = self._deconz_id + '/recall'
        await self._async_set_state_callback(field, data)

    @property
    def deconz_id(self):
        """Id to call scene over API e.g. /groups/1/scenes/1."""
        return self._deconz_id

    @property
    def full_name(self):
        """Full name."""
        return self._group_name + ' ' + self._name

    @property
    def id(self):
        """Scene ID from deCONZ."""
        return self._id

    @property
    def name(self):
        """Scene name."""
        return self._name

    def as_dict(self):
        """Callback for __dict__."""
        cdict = self.__dict__.copy()
        if '_async_set_state_callback' in cdict:
            del cdict['_async_set_state_callback']
        return cdict
