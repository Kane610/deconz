"""Test pydeCONZ light.

pytest --cov-report term-missing --cov=pydeconz.interfaces.lights --cov=pydeconz.models.light.light tests/lights/test_light.py
"""

from unittest.mock import Mock

import pytest

from pydeconz.models.light.light import (
    LightAlert,
    LightColorCapability,
    LightColorMode,
    LightEffect,
    LightFanSpeed,
)

DATA = {
    "colorcapabilities": 15,
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
        "speed": 3,
        "xy": [0.421253, 0.39921],
    },
    "swversion": "020C.201000A0",
    "type": "Extended color light",
    "uniqueid": "xx:xx:xx:xx:xx:xx:xx:xx-0A",
}


async def test_handler_light(mock_aioresponse, deconz_session, deconz_called_with):
    """Verify that creating a light works."""
    lights = deconz_session.lights.lights

    mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
    await lights.set_state(
        id="0",
        alert=LightAlert.SHORT,
        brightness=200,
        color_loop_speed=10,
        color_temperature=400,
        effect=LightEffect.COLOR_LOOP,
        fan_speed=LightFanSpeed.OFF,
        hue=1000,
        on=True,
        on_time=100,
        saturation=150,
        transition_time=250,
        xy=(0.1, 0.1),
    )
    assert deconz_called_with(
        "put",
        path="/lights/0/state",
        json={
            "alert": "select",
            "bri": 200,
            "colorloopspeed": 10,
            "ct": 400,
            "effect": "colorloop",
            "hue": 1000,
            "on": True,
            "ontime": 100,
            "speed": 0,
            "sat": 150,
            "transitiontime": 250,
            "xy": (0.1, 0.1),
        },
    )

    mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
    await lights.set_state("0", on=False)
    assert deconz_called_with(
        "put",
        path="/lights/0/state",
        json={"on": False},
    )


async def test_handler_fan(mock_aioresponse, deconz_session, deconz_called_with):
    """Verify light fixture with fan work."""
    lights = deconz_session.lights.lights

    mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
    await lights.set_state("0", fan_speed=LightFanSpeed.OFF)
    assert deconz_called_with("put", path="/lights/0/state", json={"speed": 0})

    mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
    await lights.set_state("0", fan_speed=LightFanSpeed.PERCENT_25)
    assert deconz_called_with("put", path="/lights/0/state", json={"speed": 1})

    mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
    await lights.set_state("0", fan_speed=LightFanSpeed.PERCENT_50)
    assert deconz_called_with("put", path="/lights/0/state", json={"speed": 2})

    mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
    await lights.set_state("0", fan_speed=LightFanSpeed.PERCENT_75)
    assert deconz_called_with("put", path="/lights/0/state", json={"speed": 3})

    mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
    await lights.set_state("0", fan_speed=LightFanSpeed.PERCENT_100)
    assert deconz_called_with("put", path="/lights/0/state", json={"speed": 4})

    mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
    await lights.set_state("0", fan_speed=LightFanSpeed.AUTO)
    assert deconz_called_with("put", path="/lights/0/state", json={"speed": 5})

    mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
    await lights.set_state("0", fan_speed=LightFanSpeed.COMFORT_BREEZE)
    assert deconz_called_with("put", path="/lights/0/state", json={"speed": 6})


async def test_light_light(mock_aioresponse, deconz_light, deconz_called_with):
    """Verify that creating a light works."""
    light = await deconz_light(DATA)

    assert light.state is False
    assert light.on is False
    assert light.alert == LightAlert.UNKNOWN

    assert light.brightness == 111
    assert light.hue == 7998
    assert light.saturation == 172
    assert light.color_temp == 307
    assert light.xy == (0.421253, 0.39921)
    assert light.color_mode == LightColorMode.CT
    assert light.max_color_temp == 500
    assert light.min_color_temp == 153
    assert light.effect == LightEffect.UNKNOWN
    assert light.fan_speed == LightFanSpeed.PERCENT_75
    assert light.supports_fan_speed is True
    assert (
        light.color_capabilities
        == LightColorCapability.HUE_SATURATION
        | LightColorCapability.ENHANCED_HUE
        | LightColorCapability.COLOR_LOOP
        | LightColorCapability.XY_ATTRIBUTES
        | LightColorCapability.COLOR_TEMPERATURE
    )
    assert light.reachable is True

    assert light.deconz_id == "/lights/0"
    assert light.etag == "026bcfe544ad76c7534e5ca8ed39047c"
    assert light.manufacturer == "dresden elektronik"
    assert light.model_id == "FLS-PP3"
    assert light.name == "Light 1"
    assert light.software_version == "020C.201000A0"
    assert light.type == "Extended color light"
    assert light.unique_id == "xx:xx:xx:xx:xx:xx:xx:xx-0A"

    light.register_callback(mock_callback := Mock())
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

    light.raw["ctmax"] = 1000
    assert light.max_color_temp == 650

    light.raw["ctmin"] = 0
    assert light.min_color_temp == 140

    del light.raw["ctmax"]
    assert light.max_color_temp is None

    del light.raw["ctmin"]
    assert light.min_color_temp is None

    mock_aioresponse.put("http://host:80/api/apikey/lights/0")
    await light.set_attributes(name="light")
    assert deconz_called_with(
        "put",
        path="/lights/0",
        json={"name": "light"},
    )

    mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
    await light.set_state(
        alert=LightAlert.SHORT.value,
        brightness=200,
        color_loop_speed=10,
        color_temperature=400,
        effect=LightEffect.COLOR_LOOP.value,
        hue=1000,
        on=True,
        on_time=100,
        saturation=150,
        transition_time=250,
        xy=(0.1, 0.1),
    )
    assert deconz_called_with(
        "put",
        path="/lights/0/state",
        json={
            "alert": "select",
            "bri": 200,
            "colorloopspeed": 10,
            "ct": 400,
            "effect": "colorloop",
            "hue": 1000,
            "on": True,
            "ontime": 100,
            "sat": 150,
            "transitiontime": 250,
            "xy": (0.1, 0.1),
        },
    )

    mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
    await light.set_state(on=False)
    assert deconz_called_with(
        "put",
        path="/lights/0/state",
        json={"on": False},
    )

    light.update({"state": {"bri": 2}})
    assert light.brightness == 2


ENUM_PROPERTY_DATA = [
    (
        ("state", "alert"),
        "alert",
        {
            "none": LightAlert.NONE,
            "lselect": LightAlert.LONG,
            "select": LightAlert.SHORT,
            None: LightAlert.UNKNOWN,
        },
    ),
    (
        ("colorcapabilities",),
        "color_capabilities",
        {
            0: LightColorCapability.HUE_SATURATION,
            9: LightColorCapability.UNKNOWN,
            None: LightColorCapability.UNKNOWN,
        },
    ),
    (
        ("state", "colormode"),
        "color_mode",
        {
            "ct": LightColorMode.CT,
            "hs": LightColorMode.HS,
            "xy": LightColorMode.XY,
            None: LightColorMode.UNKNOWN,
        },
    ),
    (
        ("state", "effect"),
        "effect",
        {
            "colorloop": LightEffect.COLOR_LOOP,
            "none": LightEffect.NONE,
            None: LightEffect.UNKNOWN,
        },
    ),
    (
        ("state", "speed"),
        "fan_speed",
        {
            0: LightFanSpeed.OFF,
            1: LightFanSpeed.PERCENT_25,
            2: LightFanSpeed.PERCENT_50,
            3: LightFanSpeed.PERCENT_75,
            4: LightFanSpeed.PERCENT_100,
            5: LightFanSpeed.AUTO,
            6: LightFanSpeed.COMFORT_BREEZE,
        },
    ),
]


@pytest.mark.parametrize("path, property, data", ENUM_PROPERTY_DATA)
async def test_enum_light_properties(deconz_light, path, property, data):
    """Verify enum properties return expected values or None."""
    light = await deconz_light({"config": {}, "state": {}, "type": "Color light"})

    for input, output in data.items():
        data = {path[0]: input}
        if len(path) == 2:
            data = {path[0]: {path[1]: input}}
        light.update(data)
        assert getattr(light, property) == output


async def test_enum_light_properties_no_key(deconz_light):
    """Verify enum properties return expected values or None."""
    light = await deconz_light({"config": {}, "state": {}, "type": "Color light"})

    assert light.alert is None
    assert light.color_capabilities is None
    assert light.color_mode is None
    assert light.effect is None
    with pytest.raises(KeyError):
        assert light.fan_speed
