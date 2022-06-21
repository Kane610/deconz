"""Test pydeCONZ range extender.

pytest --cov-report term-missing --cov=pydeconz.interfaces.lights --cov=pydeconz.models.light.range_extender tests/lights/test_range_extender.py
"""


async def test_range_extender(deconz_light):
    """Verify that range extender work."""
    range_extender = await deconz_light(
        {
            "etag": "62a220a6141a5956a6916633cad0d56f",
            "hascolor": False,
            "manufacturername": "IKEA of Sweden",
            "modelid": "TRADFRI signal repeater",
            "name": "Range extender 64",
            "state": {"alert": "none", "reachable": True},
            "swversion": "2.0.019",
            "type": "Range extender",
            "uniqueid": "00:0d:6f:ff:fe:9f:7f:52-01",
        }
    )

    assert range_extender.state is None
    assert range_extender.reachable is True

    assert range_extender.deconz_id == "/lights/0"
    assert range_extender.etag == "62a220a6141a5956a6916633cad0d56f"
    assert range_extender.manufacturer == "IKEA of Sweden"
    assert range_extender.model_id == "TRADFRI signal repeater"
    assert range_extender.name == "Range extender 64"
    assert range_extender.software_version == "2.0.019"
    assert range_extender.type == "Range extender"
    assert range_extender.unique_id == "00:0d:6f:ff:fe:9f:7f:52-01"
