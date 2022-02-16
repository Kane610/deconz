"""Test pydeCONZ lights.

pytest --cov-report term-missing --cov=pydeconz.light tests/test_lights.py
"""

from unittest.mock import AsyncMock, Mock

from pydeconz.interfaces.lights import LightResourceManager

from pydeconz.models.light.fan import FAN_SPEED_100_PERCENT
from pydeconz.models.light import (
    ALERT_KEY,
    ALERT_LONG,
    ALERT_NONE,
    ALERT_SHORT,
    EFFECT_COLOR_LOOP,
    ON_TIME_KEY,
)


async def test_create_light():
    """Verify that creating a light works."""
    mock_request = AsyncMock()
    lights = LightResourceManager(
        {
            "0": {
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
        },
        mock_request,
    )
    light = lights["0"]

    assert light.state is False
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
    assert light.reachable is True

    assert light.deconz_id == "/lights/0"
    assert light.etag == "026bcfe544ad76c7534e5ca8ed39047c"
    assert light.manufacturer == "dresden elektronik"
    assert light.model_id == "FLS-PP3"
    assert light.name == "Light 1"
    assert light.software_version == "020C.201000A0"
    assert light.type == "Extended color light"
    assert light.unique_id == "00:21:2E:FF:FF:00:73:9F-0A"

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

    light.raw["ctmax"] = 1000
    assert light.max_color_temp == 650

    light.raw["ctmin"] = 0
    assert light.min_color_temp == 140

    del light.raw["ctmax"]
    assert light.max_color_temp is None

    del light.raw["ctmin"]
    assert light.min_color_temp is None

    await light.set_attributes(name="light")
    mock_request.assert_called_with(
        "put",
        path="/lights/0",
        json={"name": "light"},
    )

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
    mock_request.assert_called_with(
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

    await light.set_state(on=False)
    mock_request.assert_called_with(
        "put",
        path="/lights/0/state",
        json={"on": False},
    )

    lights.process_raw({"0": {"state": {"bri": 2}}})
    assert light.brightness == 2


async def test_configuration_tool():
    """Verify that locks work."""
    lights = LightResourceManager(
        {
            "0": {
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
            }
        },
        AsyncMock(),
    )
    configuration_tool = lights["0"]

    assert configuration_tool.state is None

    assert configuration_tool.reachable is True

    assert configuration_tool.deconz_id == "/lights/0"
    assert configuration_tool.etag == "26839cb118f5bf7ba1f2108256644010"
    assert configuration_tool.manufacturer == "dresden elektronik"
    assert configuration_tool.model_id == "ConBee II"
    assert configuration_tool.name == "Configuration tool 1"
    assert configuration_tool.software_version == "0x264a0700"
    assert configuration_tool.type == "Configuration tool"
    assert configuration_tool.unique_id == "00:21:2e:ff:ff:05:a7:a3-01"


async def test_create_cover():
    """Verify that covers work."""
    mock_request = AsyncMock()
    lights = LightResourceManager(
        {
            "0": {
                "etag": "87269755b9b3a046485fdae8d96b252c",
                "hascolor": False,
                "lastannounced": None,
                "lastseen": "2020-08-01T16:22:05Z",
                "manufacturername": "AXIS",
                "modelid": "Gear",
                "name": "Covering device",
                "state": {
                    "bri": 0,
                    "lift": 0,
                    "on": False,
                    "open": True,
                    "reachable": True,
                },
                "swversion": "100-5.3.5.1122",
                "type": "Window covering device",
                "uniqueid": "00:24:46:00:00:12:34:56-01",
            }
        },
        mock_request,
    )
    cover = lights["0"]

    assert cover.state is False
    assert cover.is_open is True
    assert cover.lift == 0
    assert cover.tilt is None

    assert cover.reachable is True

    assert cover.deconz_id == "/lights/0"
    assert cover.etag == "87269755b9b3a046485fdae8d96b252c"
    assert cover.manufacturer == "AXIS"
    assert cover.model_id == "Gear"
    assert cover.name == "Covering device"
    assert cover.software_version == "100-5.3.5.1122"
    assert cover.type == "Window covering device"
    assert cover.unique_id == "00:24:46:00:00:12:34:56-01"

    mock_callback = Mock()
    cover.register_callback(mock_callback)
    assert cover._callbacks

    event = {"state": {"lift": 50, "open": True}}
    cover.update(event)
    assert cover.is_open is True
    assert cover.lift == 50
    mock_callback.assert_called_once()
    assert cover.changed_keys == {"state", "lift", "open"}

    event = {"state": {"bri": 30, "on": False}}
    cover.update(event)
    assert cover.is_open is True
    assert cover.lift == 50

    await cover.open()
    mock_request.assert_called_with("put", path="/lights/0/state", json={"open": True})

    await cover.close()
    mock_request.assert_called_with("put", path="/lights/0/state", json={"open": False})

    # Tilt not supported
    await cover.set_position(lift=30, tilt=60)
    mock_request.assert_called_with("put", path="/lights/0/state", json={"lift": 30})

    await cover.stop()
    mock_request.assert_called_with("put", path="/lights/0/state", json={"stop": True})

    # Verify tilt works as well

    cover.raw["state"]["tilt"] = 40
    assert cover.tilt == 40

    await cover.set_position(lift=20, tilt=60)
    mock_request.assert_called_with(
        "put", path="/lights/0/state", json={"lift": 20, "tilt": 60}
    )

    cover.remove_callback(mock_callback)
    assert not cover._callbacks


async def test_create_cover_without_lift():
    """Verify that covers work with older deconz versions."""
    mock_request = AsyncMock()
    lights = LightResourceManager(
        {
            "0": {
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
            }
        },
        mock_request,
    )
    cover = lights["0"]

    assert cover.state is False
    assert cover.is_open is True
    assert cover.lift == 0
    assert cover.tilt is None

    assert cover.reachable is True

    assert cover.deconz_id == "/lights/0"
    assert cover.etag == "87269755b9b3a046485fdae8d96b252c"
    assert cover.manufacturer == "AXIS"
    assert cover.model_id == "Gear"
    assert cover.name == "Covering device"
    assert cover.software_version == "100-5.3.5.1122"
    assert cover.type == "Window covering device"
    assert cover.unique_id == "00:24:46:00:00:12:34:56-01"

    mock_callback = Mock()
    cover.register_callback(mock_callback)
    assert cover._callbacks

    event = {"state": {"bri": 50, "on": True}}
    cover.update(event)
    assert cover.is_open is False
    assert cover.lift == 19
    mock_callback.assert_called_once()
    assert cover.changed_keys == {"state", "bri", "on"}

    event = {"state": {"bri": 30, "on": False}}
    cover.update(event)
    assert cover.is_open is True
    assert cover.lift == 11

    await cover.open()
    mock_request.assert_called_with("put", path="/lights/0/state", json={"on": False})

    await cover.close()
    mock_request.assert_called_with("put", path="/lights/0/state", json={"on": True})

    await cover.set_position(lift=30)
    mock_request.assert_called_with("put", path="/lights/0/state", json={"bri": 76})

    await cover.stop()
    mock_request.assert_called_with("put", path="/lights/0/state", json={"bri_inc": 0})

    # Verify sat (for tilt) works as well

    cover.raw["state"]["sat"] = 40
    assert cover.tilt == 15

    await cover.set_position(lift=20, tilt=60)
    mock_request.assert_called_with(
        "put", path="/lights/0/state", json={"bri": 50, "sat": 152}
    )

    cover.raw["state"]["lift"] = 0
    cover.raw["state"]["tilt"] = 0
    cover.raw["state"]["open"] = True

    assert cover.tilt == 0

    await cover.open()
    mock_request.assert_called_with("put", path="/lights/0/state", json={"open": True})

    await cover.close()
    mock_request.assert_called_with("put", path="/lights/0/state", json={"open": False})

    await cover.set_position(lift=20, tilt=60)
    mock_request.assert_called_with(
        "put", path="/lights/0/state", json={"lift": 20, "tilt": 60}
    )

    cover.remove_callback(mock_callback)
    assert not cover._callbacks


async def test_create_fan():
    """Verify light fixture with fan work."""
    mock_request = AsyncMock()
    lights = LightResourceManager(
        {
            "0": {
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
        },
        mock_request,
    )
    fan = lights["0"]

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

    mock_callback = Mock()
    fan.register_callback(mock_callback)
    assert fan._callbacks

    event = {"state": {"speed": 1}}
    fan.update(event)

    assert fan.brightness == 254
    assert fan.speed == 1
    mock_callback.assert_called_once()
    assert fan.changed_keys == {"state", "speed"}

    await fan.set_speed(FAN_SPEED_100_PERCENT)
    mock_request.assert_called_with("put", path="/lights/0/state", json={"speed": 4})

    fan.remove_callback(mock_callback)
    assert not fan._callbacks


async def test_create_lock():
    """Verify that locks work."""
    mock_request = AsyncMock()
    lights = LightResourceManager(
        {
            "0": {
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
            }
        },
        mock_request,
    )
    lock = lights["0"]

    assert lock.state is False
    assert lock.is_locked is False

    assert lock.reachable is True

    assert lock.deconz_id == "/lights/0"
    assert lock.etag == "5c2ec06cde4bd654aef3a555fcd8ad12"
    assert lock.manufacturer == "Danalock"
    assert lock.model_id == "V3-BTZB"
    assert lock.name == "Door lock"
    assert lock.software_version == "19042019"
    assert lock.type == "Door Lock"
    assert lock.unique_id == "00:00:00:00:00:00:00:00-00"

    mock_callback = Mock()
    lock.register_callback(mock_callback)
    assert lock._callbacks

    event = {"state": {"on": True}}
    lock.update(event)
    assert lock.is_locked is True
    mock_callback.assert_called_once()
    assert lock.changed_keys == {"state", "on"}

    await lock.lock()
    mock_request.assert_called_with("put", path="/lights/0/state", json={"on": True})

    await lock.unlock()
    mock_request.assert_called_with("put", path="/lights/0/state", json={"on": False})

    lock.remove_callback(mock_callback)
    assert not lock._callbacks


async def test_create_siren():
    """Verify that sirens work."""
    mock_request = AsyncMock()
    lights = LightResourceManager(
        {
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
            }
        },
        mock_request,
    )
    siren = lights["0"]

    assert siren.state is None
    assert siren.is_on is False

    assert siren.reachable is True

    assert siren.deconz_id == "/lights/0"
    assert siren.etag == "0667cb8fff2adc1bf22be0e6eece2a18"
    assert siren.manufacturer == "Heiman"
    assert siren.model_id == "WarningDevice"
    assert siren.name == "alarm_tuin"
    assert siren.software_version is None
    assert siren.type == "Warning device"
    assert siren.unique_id == "00:0d:6f:00:0f:ab:12:34-01"

    mock_callback = Mock()
    siren.register_callback(mock_callback)
    assert siren._callbacks

    event = {"state": {ALERT_KEY: ALERT_LONG}}
    siren.update(event)
    assert siren.is_on is True
    mock_callback.assert_called_once()
    assert siren.changed_keys == {"state", ALERT_KEY}

    await siren.turn_on()
    mock_request.assert_called_with(
        "put",
        path="/lights/0/state",
        json={ALERT_KEY: ALERT_LONG},
    )

    await siren.turn_on(duration=10)
    mock_request.assert_called_with(
        "put",
        path="/lights/0/state",
        json={ALERT_KEY: ALERT_LONG, ON_TIME_KEY: 10},
    )

    await siren.turn_off()
    mock_request.assert_called_with(
        "put",
        path="/lights/0/state",
        json={ALERT_KEY: ALERT_NONE},
    )

    siren.remove_callback(mock_callback)
    assert not siren._callbacks


async def test_create_all_light_types():
    """Verify that sirens work."""
    mock_request = AsyncMock()
    lights = LightResourceManager(
        {
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
        mock_request,
    )
    assert len(lights.keys()) == 7
    assert lights["0"].type == "Warning device"
    assert lights["1"].type == "Door Lock"
    assert lights["2"].type == "Fan"
    assert lights["3"].type == "Window covering device"
    assert lights["4"].type == "Configuration tool"
    assert lights["5"].type == "Extended color light"
    assert lights["6"].type == "unsupported device"  # legacy support
