"""Test pydeCONZ lights.

pytest --cov-report term-missing --cov=pydeconz.light tests/test_lights.py
"""

from tests import lights as light_test_data


async def test_create_all_light_types(deconz_refresh_state):
    """Verify that light types work."""
    deconz_session = await deconz_refresh_state(
        lights={
            "0": light_test_data.test_configuration_tool.DATA,
            "1": light_test_data.test_cover.DATA,
            "2": light_test_data.test_light.DATA,
            "3": light_test_data.test_lock.DATA,
            "4": light_test_data.test_siren.DATA,
            "5": {"type": "unsupported device"},
        },
    )

    lights = deconz_session.lights
    assert len(lights._handlers) == 6
    assert lights["0"].type == "Configuration tool"
    assert lights["1"].type == "Window covering device"
    assert lights["2"].type == "Extended color light"
    assert lights["3"].type == "Door Lock"
    assert lights["4"].type == "Warning device"
    assert lights["5"].type == "unsupported device"  # legacy support
