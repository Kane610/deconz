"""Test pydeCONZ light.

pytest --cov-report term-missing --cov=pydeconz.interfaces.lights --cov=pydeconz.models.light.light tests/lights/test_light.py
"""

from unittest.mock import Mock

import pytest

from pydeconz.interfaces.lights import Alert, Effect
from pydeconz.models.light import (
    ALERT_SHORT,
    EFFECT_COLOR_LOOP,
)
from pydeconz.models.light.light import ColorCapability


async def test_control_light(mock_aioresponse, deconz_session, deconz_called_with):
    """Verify that creating a light works."""
    lights = deconz_session.lights.lights

    mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
    await lights.set_state(
        id="0",
        alert=Alert.SHORT,
        brightness=200,
        color_loop_speed=10,
        color_temperature=400,
        effect=Effect.COLORLOOP,
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
    await lights.set_state("0", on=False)
    assert deconz_called_with(
        "put",
        path="/lights/0/state",
        json={"on": False},
    )


async def test_create_light(mock_aioresponse, deconz_light, deconz_called_with):
    """Verify that creating a light works."""
    light = await deconz_light(
        {
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
                "xy": [0.421253, 0.39921],
            },
            "swversion": "020C.201000A0",
            "type": "Extended color light",
            "uniqueid": "00:21:2E:FF:FF:00:73:9F-0A",
        }
    )

    assert light.state is False
    assert light.on is False
    assert light.alert is None

    assert light.brightness == 111
    assert light.hue == 7998
    assert light.saturation == 172
    assert light.color_temp == 307
    assert light.xy == (0.421253, 0.39921)
    assert light.color_mode == "ct"
    assert light.max_color_temp == 500
    assert light.min_color_temp == 153
    assert light.effect is None
    assert (
        light.color_capabilities
        == ColorCapability.HUE_SATURATION
        | ColorCapability.ENHANCED_HUE
        | ColorCapability.COLOR_LOOP
        | ColorCapability.XY_ATTRIBUTES
        | ColorCapability.COLOR_TEMPERATURE
    )
    assert light.reachable is True

    assert light.deconz_id == "/lights/0"
    assert light.etag == "026bcfe544ad76c7534e5ca8ed39047c"
    assert light.manufacturer == "dresden elektronik"
    assert light.model_id == "FLS-PP3"
    assert light.name == "Light 1"
    assert light.software_version == "020C.201000A0"
    assert light.type == "Extended color light"
    assert light.unique_id == "00:21:2E:FF:FF:00:73:9F-0A"

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
        alert=ALERT_SHORT,
        brightness=200,
        color_loop_speed=10,
        color_temperature=400,
        effect=EFFECT_COLOR_LOOP,
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
        ("colorcapabilities"),
        ("color_capabilities"),
        {
            0: ColorCapability.HUE_SATURATION,
            9: ColorCapability.UNKNOWN,
            None: ColorCapability.UNKNOWN,
        },
    ),
]


@pytest.mark.parametrize("path, property, data", ENUM_PROPERTY_DATA)
async def test_enum_thermostat_properties(deconz_light, path, property, data):
    """Verify enum properties return expected values or None."""
    light = await deconz_light({"config": {}, "state": {}, "type": "Color light"})

    assert getattr(light, property) is None

    for input, output in data.items():
        light.update({path: input})
        assert getattr(light, property) == output
