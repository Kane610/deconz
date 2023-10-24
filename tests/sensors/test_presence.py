"""Test pydeCONZ presence."""

from pydeconz.models.sensor.presence import (
    PresenceConfigDeviceMode,
    PresenceConfigTriggerDistance,
    PresenceStatePresenceEvent,
)

DATA = {
    "config": {
        "alert": "none",
        "battery": 100,
        "delay": 0,
        "ledindication": False,
        "on": True,
        "pending": [],
        "reachable": True,
        "sensitivity": 1,
        "sensitivitymax": 2,
        "usertest": False,
    },
    "ep": 2,
    "etag": "5cfb81765e86aa53ace427cfd52c6d52",
    "manufacturername": "Philips",
    "modelid": "SML001",
    "name": "Motion sensor 4",
    "state": {
        "lastupdated": "2019-05-05T14:37:06",
        "presence": False,
    },
    "swversion": "6.1.0.18912",
    "type": "ZHAPresence",
    "uniqueid": "xx:xx:xx:xx:xx:xx:xx:xx-02-0406",
}

DATA_PRESENCE_EVENT = {
    "config": {
        "devicemode": "undirected",
        "on": True,
        "reachable": True,
        "sensitivity": 3,
        "triggerdistance": "medium",
    },
    "etag": "13ff209f9401b317987d42506dd4cd79",
    "lastannounced": None,
    "lastseen": "2022-06-28T23:13Z",
    "manufacturername": "aqara",
    "modelid": "lumi.motion.ac01",
    "name": "Aqara FP1",
    "state": {
        "lastupdated": "2022-06-28T23:13:38.577",
        "presence": True,
        "presenceevent": "leave",
    },
    "swversion": "20210121",
    "type": "ZHAPresence",
    "uniqueid": "xx:xx:xx:xx:xx:xx:xx:xx-01-0406",
}


async def test_handler_presence(mock_aioresponse, deconz_session, deconz_called_with):
    """Verify that configuring presence sensor works."""
    presence = deconz_session.sensors.presence

    mock_aioresponse.put("http://host:80/api/apikey/sensors/0/config")
    await presence.set_config("0", delay=10, duration=20, sensitivity=1)
    assert deconz_called_with(
        "put",
        path="/sensors/0/config",
        json={"delay": 10, "duration": 20, "sensitivity": 1},
    )

    mock_aioresponse.put("http://host:80/api/apikey/sensors/0/config")
    await presence.set_config("0", delay=1)
    assert deconz_called_with(
        "put",
        path="/sensors/0/config",
        json={"delay": 1},
    )

    mock_aioresponse.put("http://host:80/api/apikey/sensors/0/config")
    await presence.set_config("0", duration=2)
    assert deconz_called_with(
        "put",
        path="/sensors/0/config",
        json={"duration": 2},
    )

    mock_aioresponse.put("http://host:80/api/apikey/sensors/0/config")
    await presence.set_config("0", sensitivity=3)
    assert deconz_called_with(
        "put",
        path="/sensors/0/config",
        json={"sensitivity": 3},
    )

    mock_aioresponse.put("http://host:80/api/apikey/sensors/0/config")
    await presence.set_config("0", device_mode=PresenceConfigDeviceMode.LEFT_AND_RIGHT)
    assert deconz_called_with(
        "put",
        path="/sensors/0/config",
        json={"devicemode": "leftright"},
    )

    mock_aioresponse.put("http://host:80/api/apikey/sensors/0/config")
    await presence.set_config("0", reset_presence=True)
    assert deconz_called_with(
        "put",
        path="/sensors/0/config",
        json={"resetpresence": True},
    )

    mock_aioresponse.put("http://host:80/api/apikey/sensors/0/config")
    await presence.set_config("0", trigger_distance=PresenceConfigTriggerDistance.FAR)
    assert deconz_called_with(
        "put",
        path="/sensors/0/config",
        json={"triggerdistance": "far"},
    )


async def test_sensor_presence(deconz_sensor):
    """Verify that presence sensor works."""
    sensor = await deconz_sensor(DATA)

    assert sensor.dark is None
    assert sensor.delay == 0
    assert sensor.device_mode is None
    assert sensor.duration is None
    assert sensor.presence is False
    assert sensor.presence_event is None
    assert sensor.sensitivity == 1
    assert sensor.max_sensitivity == 2
    assert sensor.trigger_distance is None

    # DeconzSensor
    assert sensor.battery == 100
    assert sensor.ep == 2
    assert sensor.low_battery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.internal_temperature is None

    # DeconzDevice
    assert sensor.deconz_id == "/sensors/0"
    assert sensor.etag == "5cfb81765e86aa53ace427cfd52c6d52"
    assert sensor.manufacturer == "Philips"
    assert sensor.model_id == "SML001"
    assert sensor.name == "Motion sensor 4"
    assert sensor.software_version == "6.1.0.18912"
    assert sensor.type == "ZHAPresence"
    assert sensor.unique_id == "xx:xx:xx:xx:xx:xx:xx:xx-02-0406"


async def test_sensor_presence_event(deconz_sensor):
    """Verify that presence event sensor works."""
    sensor = await deconz_sensor(DATA_PRESENCE_EVENT)

    assert sensor.dark is None
    assert sensor.delay is None
    assert sensor.device_mode == PresenceConfigDeviceMode.UNDIRECTED
    assert sensor.duration is None
    assert sensor.presence is True
    assert sensor.presence_event == PresenceStatePresenceEvent.LEAVE
    assert sensor.sensitivity == 3
    assert sensor.max_sensitivity is None
    assert sensor.trigger_distance == PresenceConfigTriggerDistance.MEDIUM

    # DeconzSensor
    assert sensor.battery is None
    assert sensor.ep is None
    assert sensor.low_battery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.internal_temperature is None

    # DeconzDevice
    assert sensor.deconz_id == "/sensors/0"
    assert sensor.etag == "13ff209f9401b317987d42506dd4cd79"
    assert sensor.manufacturer == "aqara"
    assert sensor.model_id == "lumi.motion.ac01"
    assert sensor.name == "Aqara FP1"
    assert sensor.software_version == "20210121"
    assert sensor.type == "ZHAPresence"
    assert sensor.unique_id == "xx:xx:xx:xx:xx:xx:xx:xx-01-0406"
