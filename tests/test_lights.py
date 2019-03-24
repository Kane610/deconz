"""Test pydeCONZ lights.

pytest --cov-report term-missing --cov=pydeconz.light tests/test_lights.py
"""

from unittest.mock import Mock

from pydeconz.light import DeconzLight


async def test_create_light():
    """Verify that creating a light works.

    Just tests a subset right now;
        xy will also be signalled as a set from 0.61.
    """
    light = DeconzLight('0', FIXTURE_RGB_LIGHT, None)

    mock_callback = Mock()
    light.register_async_callback(mock_callback)
    assert light._async_callbacks

    assert light.xy == (0.421253, 0.39921)

    event = {"state": {
        "lastupdated": "2019-03-15T10:15:17",
        "x": 0.1,
        "y": 0.1
    }}
    light.async_update(event)

    assert light.xy == (0.1, 0.1)
    mock_callback.assert_called_with({})

    event = {"state": {
        "lastupdated": "2019-03-15T10:15:17",
        "xy": [0.2, 0.2],
        "x": 0.1,
        "y": 0.1
    }}
    light.async_update(event)

    assert light.xy == (0.2, 0.2)

    event = {"state": {
        "lastupdated": "2019-03-15T10:15:17",
        "x": 0.1,
        "y": 0.1
    }}
    light.async_update(event)

    assert light.xy == (0.2, 0.2)

    light.remove_callback(mock_callback)
    assert not light._async_callbacks


FIXTURE_RGB_LIGHT = {
    "etag": "026bcfe544ad76c7534e5ca8ed39047c",
    "hascolor": True,
    "manufacturer": "dresden elektronik",
    "modelid": "FLS-PP3",
    "name": "Light 1",
    "pointsymbol": {},
    "state": {
        "alert": None,
        "bri": 111,
        "colormode": "ct",
        "ct": 307,
        "effect": None,
        "hue": 7998,
        "on": False,
        "reachable": True,
        "sat": 172,
        "xy": [0.421253, 0.39921],
    },
    "swversion": "020C.201000A0",
    "type": "Extended color light",
    "uniqueid": "00:21:2E:FF:FF:00:73:9F-0A"
}
