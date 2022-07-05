"""Test pydeCONZ configuration tool.

pytest --cov-report term-missing --cov=pydeconz.interfaces.lights --cov=pydeconz.models.light.configuration_tool tests/lights/test_configuration_tool.py
"""

DATA = {
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
    "uniqueid": "xx:xx:xx:xx:xx:xx:xx:xx-01",
}


async def test_light_configuration_tool(deconz_light):
    """Verify that configuration tool work."""
    configuration_tool = await deconz_light(DATA)

    assert configuration_tool.state is None
    assert configuration_tool.reachable is True

    assert configuration_tool.deconz_id == "/lights/0"
    assert configuration_tool.etag == "26839cb118f5bf7ba1f2108256644010"
    assert configuration_tool.manufacturer == "dresden elektronik"
    assert configuration_tool.model_id == "ConBee II"
    assert configuration_tool.name == "Configuration tool 1"
    assert configuration_tool.software_version == "0x264a0700"
    assert configuration_tool.type == "Configuration tool"
    assert configuration_tool.unique_id == "xx:xx:xx:xx:xx:xx:xx:xx-01"
