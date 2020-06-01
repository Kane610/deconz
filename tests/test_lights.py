"""Test pydeCONZ lights.

pytest --cov-report term-missing --cov=pydeconz.light tests/test_lights.py
"""

from copy import deepcopy
from unittest.mock import Mock

from pydeconz.light import DeconzLight


async def test_create_light():
    """Verify that creating a light works.

    Just tests a subset right now;
        xy will also be signalled as a set from 0.61.
    """
    light = DeconzLight("0", deepcopy(FIXTURE_RGB_LIGHT), None)

    assert light.state is False
    assert light.alert is None

    assert light.brightness == 111
    assert light.hue == 7998
    assert light.sat == 172
    assert light.ct == 307
    assert light.xy == (0.421253, 0.39921)
    assert light.colormode == "ct"
    assert light.ctmax == 500
    assert light.ctmin == 153
    assert light.effect is None
    assert light.hascolor is True
    assert light.reachable is True

    assert light.deconz_id == "/lights/0"
    assert light.etag == "026bcfe544ad76c7534e5ca8ed39047c"
    assert light.manufacturer == "dresden elektronik"
    assert light.modelid == "FLS-PP3"
    assert light.name == "Light 1"
    assert light.swversion == "020C.201000A0"
    assert light.type == "Extended color light"
    assert light.uniqueid == "00:21:2E:FF:FF:00:73:9F-0A"

    mock_callback = Mock()
    light.register_callback(mock_callback)
    assert light._callbacks

    event = {"state": {"xy": [0.1, 0.1]}}
    light.update(event)

    assert light.brightness == 111
    assert light.xy == (0.1, 0.1)
    mock_callback.assert_called_once()
    assert light.changed_keys == {"state", "xy"}

    light.remove_callback(mock_callback)
    assert not light._callbacks

    light.raw["state"]["xy"] = (65555, 65555)
    assert light.xy == (1, 1)

    del light.raw["state"]["xy"]
    assert light.xy is None


FIXTURE_RGB_LIGHT = {
    "ctmax": 500,
    "ctmin": 153,
    "etag": "026bcfe544ad76c7534e5ca8ed39047c",
    "hascolor": True,
    "manufacturername": "dresden elektronik",
    "modelid": "FLS-PP3",
    "name": "Light 1",
    "pointsymbol": {},
    "state": {
        "alert": None,
        "bri": 111,
        "colormode": "ct",
        "ct": 307,
        "effect": None,
        "hascolor": True,
        "hue": 7998,
        "on": False,
        "reachable": True,
        "sat": 172,
        "xy": [0.421253, 0.39921],
    },
    "swversion": "020C.201000A0",
    "type": "Extended color light",
    "uniqueid": "00:21:2E:FF:FF:00:73:9F-0A",
}
