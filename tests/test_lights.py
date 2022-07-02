"""Test pydeCONZ lights.

pytest --cov-report term-missing --cov=pydeconz.light tests/test_lights.py
"""

# from unittest.mock import Mock

import pytest

from tests import lights as light_test_data

# from pydeconz.interfaces.lights import FanSpeed
# from pydeconz.models.light.fan import FAN_SPEED_100_PERCENT


@pytest.fixture
def deconz_light(deconz_refresh_state):
    """Comfort fixture to initialize deCONZ light."""

    async def data_to_deconz_session(light):
        """Initialize deCONZ light."""
        deconz_session = await deconz_refresh_state(lights={"0": light})
        return deconz_session.lights["0"]

    yield data_to_deconz_session


# async def test_control_fan(mock_aioresponse, deconz_session, deconz_called_with):
#     """Verify light fixture with fan work."""
#     fans = deconz_session.lights.fans

#     mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
#     await fans.set_state("0", FanSpeed.OFF)
#     assert deconz_called_with("put", path="/lights/0/state", json={"speed": 0})

#     mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
#     await fans.set_state("0", FanSpeed.PERCENT_25)
#     assert deconz_called_with("put", path="/lights/0/state", json={"speed": 1})

#     mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
#     await fans.set_state("0", FanSpeed.PERCENT_50)
#     assert deconz_called_with("put", path="/lights/0/state", json={"speed": 2})

#     mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
#     await fans.set_state("0", FanSpeed.PERCENT_75)
#     assert deconz_called_with("put", path="/lights/0/state", json={"speed": 3})

#     mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
#     await fans.set_state("0", FanSpeed.PERCENT_100)
#     assert deconz_called_with("put", path="/lights/0/state", json={"speed": 4})

#     mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
#     await fans.set_state("0", FanSpeed.AUTO)
#     assert deconz_called_with("put", path="/lights/0/state", json={"speed": 5})

#     mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
#     await fans.set_state("0", FanSpeed.COMFORT_BREEZE)
#     assert deconz_called_with("put", path="/lights/0/state", json={"speed": 6})


# async def test_create_fan(mock_aioresponse, deconz_light, deconz_called_with):
#     """Verify light fixture with fan work."""
#     fan = await deconz_light(
#         {
#             "etag": "432f3de28965052961a99e3c5494daf4",
#             "hascolor": False,
#             "manufacturername": "King Of Fans,  Inc.",
#             "modelid": "HDC52EastwindFan",
#             "name": "Ceiling fan",
#             "state": {
#                 "alert": "none",
#                 "bri": 254,
#                 "on": False,
#                 "reachable": True,
#                 "speed": 4,
#             },
#             "swversion": "0000000F",
#             "type": "Fan",
#             "uniqueid": "00:22:a3:00:00:27:8b:81-01",
#         }
#     )

#     assert fan.state is False
#     assert fan.alert == "none"

#     assert fan.brightness == 254
#     assert fan.hue is None
#     assert fan.saturation is None
#     assert fan.color_temp is None
#     assert fan.xy is None
#     assert fan.color_mode is None
#     assert fan.max_color_temp is None
#     assert fan.min_color_temp is None
#     assert fan.effect is None
#     assert fan.reachable is True
#     assert fan.speed == 4

#     assert fan.deconz_id == "/lights/0"
#     assert fan.etag == "432f3de28965052961a99e3c5494daf4"
#     assert fan.manufacturer == "King Of Fans,  Inc."
#     assert fan.model_id == "HDC52EastwindFan"
#     assert fan.name == "Ceiling fan"
#     assert fan.software_version == "0000000F"
#     assert fan.type == "Fan"
#     assert fan.unique_id == "00:22:a3:00:00:27:8b:81-01"

#     fan.register_callback(mock_callback := Mock())
#     assert fan._callbacks

#     event = {"state": {"speed": 1}}
#     fan.update(event)

#     assert fan.brightness == 254
#     assert fan.speed == 1
#     mock_callback.assert_called_once()
#     assert fan.changed_keys == {"state", "speed"}

#     mock_aioresponse.put("http://host:80/api/apikey/lights/0/state")
#     await fan.set_speed(FAN_SPEED_100_PERCENT)
#     assert deconz_called_with("put", path="/lights/0/state", json={"speed": 4})

#     fan.remove_callback(mock_callback)
#     assert not fan._callbacks


async def test_create_all_light_types(deconz_refresh_state):
    """Verify that light types work."""
    deconz_session = await deconz_refresh_state(
        lights={
            "0": light_test_data.test_configuration_tool.DATA,
            "1": light_test_data.test_cover.DATA,
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
            "3": light_test_data.test_light.DATA,
            "4": light_test_data.test_lock.DATA,
            "5": light_test_data.test_siren.DATA,
            "6": {"type": "unsupported device"},
        },
    )

    lights = deconz_session.lights
    assert len(lights.keys()) == 7
    assert lights["0"].type == "Configuration tool"
    assert lights["1"].type == "Window covering device"
    assert lights["2"].type == "Fan"
    assert lights["3"].type == "Extended color light"
    assert lights["4"].type == "Door Lock"
    assert lights["5"].type == "Warning device"
    assert lights["6"].type == "unsupported device"  # legacy support
