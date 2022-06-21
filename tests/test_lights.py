"""Test pydeCONZ lights.

pytest --cov-report term-missing --cov=pydeconz.light tests/test_lights.py
"""

from unittest.mock import Mock

import pytest

from pydeconz.interfaces.lights import FanSpeed
from pydeconz.models.light.fan import FAN_SPEED_100_PERCENT


@pytest.fixture
def deconz_light(deconz_refresh_state):
    """Comfort fixture to initialize deCONZ light."""

    async def data_to_deconz_session(light):
        """Initialize deCONZ light."""
        deconz_session = await deconz_refresh_state(lights={"0": light})
        return deconz_session.lights["0"]

    yield data_to_deconz_session


async def test_control_fan(mock_aioresponse, deconz_session, deconz_called_with):
    """Verify light fixture with fan work."""
    fans = deconz_session.lights.fans

    mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
    await fans.set_state("0", FanSpeed.OFF)
    assert deconz_called_with("put", path="/lights/0/state", json={"speed": 0})

    mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
    await fans.set_state("0", FanSpeed.PERCENT_25)
    assert deconz_called_with("put", path="/lights/0/state", json={"speed": 1})

    mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
    await fans.set_state("0", FanSpeed.PERCENT_50)
    assert deconz_called_with("put", path="/lights/0/state", json={"speed": 2})

    mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
    await fans.set_state("0", FanSpeed.PERCENT_75)
    assert deconz_called_with("put", path="/lights/0/state", json={"speed": 3})

    mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
    await fans.set_state("0", FanSpeed.PERCENT_100)
    assert deconz_called_with("put", path="/lights/0/state", json={"speed": 4})

    mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
    await fans.set_state("0", FanSpeed.AUTO)
    assert deconz_called_with("put", path="/lights/0/state", json={"speed": 5})

    mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
    await fans.set_state("0", FanSpeed.COMFORT_BREEZE)
    assert deconz_called_with("put", path="/lights/0/state", json={"speed": 6})


async def test_create_fan(mock_aioresponse, deconz_light, deconz_called_with):
    """Verify light fixture with fan work."""
    fan = await deconz_light(
        {
            "etag": "432f3de28965052961a99e3c5494daf4",
            "hascolor": False,
            "manufacturername": "King Of Fans,  Inc.",
            "modelid": "HDC52EastwindFan",
            "name": "Ceiling fan",
            "state": {
                "alert": "none",
                "bri": 254,
                "on": False,
                "reachable": True,
                "speed": 4,
            },
            "swversion": "0000000F",
            "type": "Fan",
            "uniqueid": "00:22:a3:00:00:27:8b:81-01",
        }
    )

    assert fan.state is False
    assert fan.alert == "none"

    assert fan.brightness == 254
    assert fan.hue is None
    assert fan.saturation is None
    assert fan.color_temp is None
    assert fan.xy is None
    assert fan.color_mode is None
    assert fan.max_color_temp is None
    assert fan.min_color_temp is None
    assert fan.effect is None
    assert fan.reachable is True
    assert fan.speed == 4

    assert fan.deconz_id == "/lights/0"
    assert fan.etag == "432f3de28965052961a99e3c5494daf4"
    assert fan.manufacturer == "King Of Fans,  Inc."
    assert fan.model_id == "HDC52EastwindFan"
    assert fan.name == "Ceiling fan"
    assert fan.software_version == "0000000F"
    assert fan.type == "Fan"
    assert fan.unique_id == "00:22:a3:00:00:27:8b:81-01"

    fan.register_callback(mock_callback := Mock())
    assert fan._callbacks

    event = {"state": {"speed": 1}}
    fan.update(event)

    assert fan.brightness == 254
    assert fan.speed == 1
    mock_callback.assert_called_once()
    assert fan.changed_keys == {"state", "speed"}

    mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
    await fan.set_speed(FAN_SPEED_100_PERCENT)
    assert deconz_called_with("put", path="/lights/0/state", json={"speed": 4})

    fan.remove_callback(mock_callback)
    assert not fan._callbacks


async def test_create_all_light_types(deconz_refresh_state):
    """Verify that light types work."""
    deconz_session = await deconz_refresh_state(
        lights={
            "0": {
                "etag": "0667cb8fff2adc1bf22be0e6eece2a18",
                "hascolor": False,
                "manufacturername": "Heiman",
                "modelid": "WarningDevice",
                "name": "alarm_tuin",
                "state": {"alert": "none", "reachable": True},
                "swversion": None,
                "type": "Warning device",
                "uniqueid": "00:0d:6f:00:0f:ab:12:34-01",
            },
            "1": {
                "etag": "5c2ec06cde4bd654aef3a555fcd8ad12",
                "hascolor": False,
                "lastannounced": None,
                "lastseen": "2020-08-22T15:29:03Z",
                "manufacturername": "Danalock",
                "modelid": "V3-BTZB",
                "name": "Door lock",
                "state": {"alert": "none", "on": False, "reachable": True},
                "swversion": "19042019",
                "type": "Door Lock",
                "uniqueid": "00:00:00:00:00:00:00:00-00",
            },
            "2": {
                "etag": "432f3de28965052961a99e3c5494daf4",
                "hascolor": False,
                "manufacturername": "King Of Fans,  Inc.",
                "modelid": "HDC52EastwindFan",
                "name": "Ceiling fan",
                "state": {
                    "alert": "none",
                    "bri": 254,
                    "on": False,
                    "reachable": True,
                    "speed": 4,
                },
                "swversion": "0000000F",
                "type": "Fan",
                "uniqueid": "00:22:a3:00:00:27:8b:81-01",
            },
            "3": {
                "etag": "87269755b9b3a046485fdae8d96b252c",
                "hascolor": False,
                "lastannounced": None,
                "lastseen": "2020-08-01T16:22:05Z",
                "manufacturername": "AXIS",
                "modelid": "Gear",
                "name": "Covering device",
                "state": {"bri": 0, "on": False, "reachable": True},
                "swversion": "100-5.3.5.1122",
                "type": "Window covering device",
                "uniqueid": "00:24:46:00:00:12:34:56-01",
            },
            "4": {
                "etag": "26839cb118f5bf7ba1f2108256644010",
                "hascolor": False,
                "lastannounced": None,
                "lastseen": "2020-11-22T11:27Z",
                "manufacturername": "dresden elektronik",
                "modelid": "ConBee II",
                "name": "Configuration tool 1",
                "state": {"reachable": True},
                "swversion": "0x264a0700",
                "type": "Configuration tool",
                "uniqueid": "00:21:2e:ff:ff:05:a7:a3-01",
            },
            "5": {
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
            },
            "6": {"type": "unsupported device"},
        },
    )

    lights = deconz_session.lights
    assert len(lights.keys()) == 7
    assert lights["0"].type == "Warning device"
    assert lights["1"].type == "Door Lock"
    assert lights["2"].type == "Fan"
    assert lights["3"].type == "Window covering device"
    assert lights["4"].type == "Configuration tool"
    assert lights["5"].type == "Extended color light"
    assert lights["6"].type == "unsupported device"  # legacy support
