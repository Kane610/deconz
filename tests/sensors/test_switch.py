"""Test pydeCONZ switch.

pytest --cov-report term-missing --cov=pydeconz.interfaces.sensors --cov=pydeconz.models.sensor.switch tests/sensors/test_switch.py
"""

from pydeconz.models.sensor.switch import (
    SwitchDeviceMode,
    SwitchMode,
    SwitchWindowCoveringType,
)

DATA = {
    "config": {
        "battery": 90,
        "group": "201",
        "on": True,
        "reachable": True,
    },
    "ep": 2,
    "etag": "233ae541bbb7ac98c42977753884b8d2",
    "manufacturername": "Philips",
    "mode": 1,
    "modelid": "RWL021",
    "name": "Dimmer switch 3",
    "state": {
        "buttonevent": 1002,
        "lastupdated": "2019-04-28T20:29:13",
    },
    "swversion": "5.45.1.17846",
    "type": "ZHASwitch",
    "uniqueid": "00:17:88:01:02:0e:32:a3-02-fc00",
}

DATA_CUBE = {
    "config": {
        "battery": 90,
        "on": True,
        "reachable": True,
        "temperature": 1100,
    },
    "ep": 3,
    "etag": "e34fa1c7a19d960e35a1f4d56ac475af",
    "manufacturername": "LUMI",
    "mode": 1,
    "modelid": "lumi.sensor_cube.aqgl01",
    "name": "Mi Magic Cube",
    "state": {
        "buttonevent": 747,
        "gesture": 7,
        "lastupdated": "2019-12-12T18:50:40",
    },
    "swversion": "20160704",
    "type": "ZHASwitch",
    "uniqueid": "00:15:8d:00:02:8b:3b:24-03-000c",
}
DATA_HUE_WALL_SWITCH = {
    "config": {
        "battery": 100,
        "devicemode": "dualrocker",
        "on": True,
        "pending": [],
        "reachable": True,
    },
    "ep": 1,
    "etag": "01173dc5b19bb0a976006eee8d0d3718",
    "lastseen": "2021-03-12T22:55Z",
    "manufacturername": "Signify Netherlands B.V.",
    "mode": 1,
    "modelid": "RDM001",
    "name": "RDM001 15",
    "state": {
        "buttonevent": 1002,
        "eventduration": 1,
        "lastupdated": "2021-03-12T22:21:20.017",
    },
    "swversion": "20210115",
    "type": "ZHASwitch",
    "uniqueid": "00:17:88:01:0b:00:05:5d-01-fc00",
}

DATA_TINT_REMOTE = {
    "config": {
        "group": "16388,16389,16390",
        "on": True,
        "reachable": True,
    },
    "ep": 1,
    "etag": "b1336f750d31300afa441a04f2c69b68",
    "manufacturername": "MLI",
    "mode": 1,
    "modelid": "ZBT-Remote-ALL-RGBW",
    "name": "ZHA Remote 1",
    "state": {
        "angle": 10,
        "buttonevent": 6002,
        "lastupdated": "2020-09-08T18:58:24.193",
        "xy": [0.3381, 0.1627],
    },
    "swversion": "2.0",
    "type": "ZHASwitch",
    "uniqueid": "00:11:22:33:44:55:66:77-01-1000",
}

DATA_UBISYS_J1 = {
    "config": {
        "mode": "momentary",
        "on": True,
        "reachable": False,
        "windowcoveringtype": 0,
    },
    "ep": 2,
    "etag": "da5fbb89eca4133b6949537e73b31f77",
    "lastseen": "2020-11-21T15:47Z",
    "manufacturername": "ubisys",
    "mode": 1,
    "modelid": "J1 (5502)",
    "name": "J1",
    "state": {
        "buttonevent": None,
        "lastupdated": "none",
    },
    "swversion": "20190129-DE-FB0",
    "type": "ZHASwitch",
    "uniqueid": "00:1f:ee:00:00:00:00:09-02-0102",
}


async def test_handler_switch(mock_aioresponse, deconz_session, deconz_called_with):
    """Verify that configuring presence sensor works."""
    switch = deconz_session.sensors.switch

    mock_aioresponse.put("http://host:80/api/apikey/sensors/0/config")
    await switch.set_config("0", device_mode=SwitchDeviceMode.DUAL_ROCKER)
    assert deconz_called_with(
        "put",
        path="/sensors/0/config",
        json={"devicemode": "dualrocker"},
    )

    mock_aioresponse.put("http://host:80/api/apikey/sensors/0/config")
    await switch.set_config("0", mode=SwitchMode.ROCKER)
    assert deconz_called_with(
        "put",
        path="/sensors/0/config",
        json={"mode": "rocker"},
    )

    mock_aioresponse.put("http://host:80/api/apikey/sensors/0/config")
    await switch.set_config("0", window_covering_type=SwitchWindowCoveringType.DRAPERY)
    assert deconz_called_with(
        "put",
        path="/sensors/0/config",
        json={"windowcoveringtype": 4},
    )


async def test_sensor_switch(deconz_sensor):
    """Verify that switch sensor works."""
    sensor = await deconz_sensor(DATA)

    assert sensor.ZHATYPE == ("ZHASwitch", "ZGPSwitch", "CLIPSwitch")

    assert sensor.button_event == 1002
    assert sensor.gesture is None
    assert sensor.angle is None
    assert sensor.xy is None
    assert sensor.device_mode is None

    # DeconzSensor
    assert sensor.battery == 90
    assert sensor.ep == 2
    assert sensor.low_battery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.secondary_temperature is None

    # DeconzDevice
    assert sensor.deconz_id == "/sensors/0"
    assert sensor.etag == "233ae541bbb7ac98c42977753884b8d2"
    assert sensor.manufacturer == "Philips"
    assert sensor.model_id == "RWL021"
    assert sensor.name == "Dimmer switch 3"
    assert sensor.software_version == "5.45.1.17846"
    assert sensor.type == "ZHASwitch"
    assert sensor.unique_id == "00:17:88:01:02:0e:32:a3-02-fc00"


async def test_sensor_switch_sensor_cube(deconz_sensor):
    """Verify that cube switch sensor works."""
    sensor = await deconz_sensor(DATA_CUBE)

    assert sensor.ZHATYPE == ("ZHASwitch", "ZGPSwitch", "CLIPSwitch")

    assert sensor.button_event == 747
    assert sensor.gesture == 7

    # DeconzSensor
    assert sensor.battery == 90
    assert sensor.ep == 3
    assert sensor.low_battery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.secondary_temperature == 11.0

    # DeconzDevice
    assert sensor.deconz_id == "/sensors/0"
    assert sensor.etag == "e34fa1c7a19d960e35a1f4d56ac475af"
    assert sensor.manufacturer == "LUMI"
    assert sensor.model_id == "lumi.sensor_cube.aqgl01"
    assert sensor.name == "Mi Magic Cube"
    assert sensor.software_version == "20160704"
    assert sensor.type == "ZHASwitch"
    assert sensor.unique_id == "00:15:8d:00:02:8b:3b:24-03-000c"


async def test_sensor_switch_hue_wall_switch_module(deconz_sensor):
    """Verify that cube switch sensor works."""
    sensor = await deconz_sensor(DATA_HUE_WALL_SWITCH)

    assert sensor.ZHATYPE == ("ZHASwitch", "ZGPSwitch", "CLIPSwitch")

    assert sensor.button_event == 1002
    assert sensor.event_duration == 1
    assert sensor.device_mode == SwitchDeviceMode.DUAL_ROCKER
    assert not sensor.angle
    assert not sensor.gesture
    assert not sensor.mode
    assert not sensor.window_covering_type
    assert not sensor.xy

    # DeconzSensor
    assert sensor.battery == 100
    assert sensor.ep == 1
    assert not sensor.low_battery
    assert sensor.on
    assert sensor.reachable
    assert not sensor.tampered
    assert not sensor.secondary_temperature

    # DeconzDevice
    assert sensor.deconz_id == "/sensors/0"
    assert sensor.etag == "01173dc5b19bb0a976006eee8d0d3718"
    assert sensor.manufacturer == "Signify Netherlands B.V."
    assert sensor.model_id == "RDM001"
    assert sensor.name == "RDM001 15"
    assert sensor.software_version == "20210115"
    assert sensor.type == "ZHASwitch"
    assert sensor.unique_id == "00:17:88:01:0b:00:05:5d-01-fc00"


async def test_sensor_switch_tint_remote(deconz_sensor):
    """Verify that tint remote sensor works."""
    sensor = await deconz_sensor(DATA_TINT_REMOTE)

    assert sensor.ZHATYPE == ("ZHASwitch", "ZGPSwitch", "CLIPSwitch")

    assert sensor.button_event == 6002
    assert sensor.angle == 10
    assert sensor.xy == [0.3381, 0.1627]

    # DeconzSensor
    assert sensor.ep == 1
    assert sensor.low_battery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None

    # DeconzDevice
    assert sensor.deconz_id == "/sensors/0"
    assert sensor.etag == "b1336f750d31300afa441a04f2c69b68"
    assert sensor.manufacturer == "MLI"
    assert sensor.model_id == "ZBT-Remote-ALL-RGBW"
    assert sensor.name == "ZHA Remote 1"
    assert sensor.software_version == "2.0"
    assert sensor.type == "ZHASwitch"
    assert sensor.unique_id == "00:11:22:33:44:55:66:77-01-1000"


async def test_sensor_switch_ubisys_j1(deconz_sensor):
    """Verify that tint remote sensor works."""
    sensor = await deconz_sensor(DATA_UBISYS_J1)

    assert sensor.ZHATYPE == ("ZHASwitch", "ZGPSwitch", "CLIPSwitch")

    assert sensor.button_event is None
    assert sensor.angle is None
    assert sensor.xy is None
    assert sensor.mode == SwitchMode.MOMENTARY
    assert sensor.window_covering_type == SwitchWindowCoveringType.ROLLER_SHADE

    # DeconzSensor
    assert sensor.ep == 2
    assert sensor.low_battery is None
    assert sensor.on is True
    assert sensor.reachable is False
    assert sensor.tampered is None

    # DeconzDevice
    assert sensor.deconz_id == "/sensors/0"
    assert sensor.etag == "da5fbb89eca4133b6949537e73b31f77"
    assert sensor.manufacturer == "ubisys"
    assert sensor.model_id == "J1 (5502)"
    assert sensor.name == "J1"
    assert sensor.software_version == "20190129-DE-FB0"
    assert sensor.type == "ZHASwitch"
    assert sensor.unique_id == "00:1f:ee:00:00:00:00:09-02-0102"
