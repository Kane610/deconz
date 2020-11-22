"""Test pydeCONZ sensors.

pytest --cov-report term-missing --cov=pydeconz.sensor tests/test_sensors.py
"""

from unittest.mock import AsyncMock, Mock

from pydeconz.sensor import SENSOR_CLASSES, Thermostat, create_sensor, Sensors


async def test_create_sensor():
    """Verify that create-sensor can create all types."""
    assert len(SENSOR_CLASSES) == 21

    for sensor_class in SENSOR_CLASSES:
        for sensor_type in sensor_class.ZHATYPE:
            sensor = {"type": sensor_type, "config": {}, "state": {}}
            result = create_sensor("0", sensor, None)

            assert result


async def test_create_sensor_fails():
    """Verify failing behavior for create_sensor."""
    sensor_id = "0"
    sensor = {"type": "not supported", "name": "name", "state": {}, "config": {}}
    result = create_sensor(sensor_id, sensor, None)

    assert result.BINARY is False
    assert not result.ZHATYPE
    assert result.state is None


async def test_air_quality_sensor():
    """Verify that air quality sensor works."""
    sensors = Sensors(
        {
            "0": {
                "config": {"on": True, "reachable": True},
                "ep": 2,
                "etag": "c2d2e42396f7c78e11e46c66e2ec0200",
                "lastseen": "2020-11-20T22:48Z",
                "manufacturername": "BOSCH",
                "modelid": "AIR",
                "name": "BOSCH Air quality sensor",
                "state": {
                    "airquality": "poor",
                    "airqualityppb": 809,
                    "lastupdated": "2020-11-20T22:48:00.209",
                },
                "swversion": "20200402",
                "type": "ZHAAirQuality",
                "uniqueid": "00:12:4b:00:14:4d:00:07-02-fdef",
            },
        },
        AsyncMock(),
    )
    sensor = sensors["0"]

    assert sensor.BINARY is False
    assert sensor.ZHATYPE == ("ZHAAirQuality",)

    assert sensor.state == "poor"
    assert sensor.airquality == "poor"
    assert sensor.airqualityppb == 809

    # DeconzSensor
    assert sensor.battery is None
    assert sensor.ep == 2
    assert sensor.lowbattery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.secondary_temperature is None

    # DeconzDevice
    assert sensor.deconz_id == "/sensors/0"
    assert sensor.etag == "c2d2e42396f7c78e11e46c66e2ec0200"
    assert sensor.manufacturer == "BOSCH"
    assert sensor.modelid == "AIR"
    assert sensor.name == "BOSCH Air quality sensor"
    assert sensor.swversion == "20200402"
    assert sensor.type == "ZHAAirQuality"
    assert sensor.uniqueid == "00:12:4b:00:14:4d:00:07-02-fdef"


async def test_alarm_sensor():
    """Verify that alarm sensor works."""
    sensors = Sensors(
        {
            "0": {
                "config": {
                    "battery": 100,
                    "on": True,
                    "reachable": True,
                    "temperature": 2600,
                },
                "ep": 1,
                "etag": "18c0f3c2100904e31a7f938db2ba9ba9",
                "manufacturername": "dresden elektronik",
                "modelid": "lumi.sensor_motion.aq2",
                "name": "Alarm 10",
                "state": {
                    "alarm": False,
                    "lastupdated": "none",
                    "lowbattery": None,
                    "tampered": None,
                },
                "swversion": "20170627",
                "type": "ZHAAlarm",
                "uniqueid": "00:15:8d:00:02:b5:d1:80-01-0500",
            },
        },
        AsyncMock(),
    )
    sensor = sensors["0"]

    assert sensor.BINARY is True
    assert sensor.ZHATYPE == ("ZHAAlarm",)

    assert sensor.state is False
    assert sensor.alarm is False

    # DeconzSensor
    assert sensor.battery == 100
    assert sensor.ep == 1
    assert sensor.lowbattery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.secondary_temperature == 26

    # DeconzDevice
    assert sensor.deconz_id == "/sensors/0"
    assert sensor.etag == "18c0f3c2100904e31a7f938db2ba9ba9"
    assert sensor.manufacturer == "dresden elektronik"
    assert sensor.modelid == "lumi.sensor_motion.aq2"
    assert sensor.name == "Alarm 10"
    assert sensor.swversion == "20170627"
    assert sensor.type == "ZHAAlarm"
    assert sensor.uniqueid == "00:15:8d:00:02:b5:d1:80-01-0500"


async def test_battery_sensor():
    """Verify that alarm sensor works."""
    # sensor = create_sensor("0", FIXTURE_BATTERY, None)
    sensors = Sensors(
        {
            "0": {
                "config": {"alert": "none", "on": True, "reachable": True},
                "ep": 1,
                "etag": "23a8659f1cb22df2f51bc2da0e241bb4",
                "manufacturername": "IKEA of Sweden",
                "modelid": "FYRTUR block-out roller blind",
                "name": "FYRTUR block-out roller blind",
                "state": {"battery": 100, "lastupdated": "none"},
                "swversion": "2.2.007",
                "type": "ZHABattery",
                "uniqueid": "00:0d:6f:ff:fe:01:23:45-01-0001",
            },
        },
        AsyncMock(),
    )
    sensor = sensors["0"]

    assert sensor.BINARY is False
    assert sensor.ZHATYPE == ("ZHABattery",)

    assert sensor.state == 100

    # DeconzSensor
    assert sensor.battery == 100
    assert sensor.ep == 1
    assert sensor.lowbattery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.secondary_temperature is None

    # DeconzDevice
    assert sensor.deconz_id == "/sensors/0"
    assert sensor.etag == "23a8659f1cb22df2f51bc2da0e241bb4"
    assert sensor.manufacturer == "IKEA of Sweden"
    assert sensor.modelid == "FYRTUR block-out roller blind"
    assert sensor.name == "FYRTUR block-out roller blind"
    assert sensor.swversion == "2.2.007"
    assert sensor.type == "ZHABattery"
    assert sensor.uniqueid == "00:0d:6f:ff:fe:01:23:45-01-0001"


async def test_carbonmonoxide_sensor():
    """Verify that carbon monoxide sensor works."""
    sensors = Sensors(
        {
            "0": {
                "config": {
                    "battery": 100,
                    "on": True,
                    "pending": [],
                    "reachable": True,
                },
                "ep": 1,
                "etag": "b7599df551944df97b2aa87d160b9c45",
                "manufacturername": "Heiman",
                "modelid": "CO_V16",
                "name": "Cave, CO",
                "state": {
                    "carbonmonoxide": False,
                    "lastupdated": "none",
                    "lowbattery": False,
                    "tampered": False,
                },
                "swversion": "20150330",
                "type": "ZHACarbonMonoxide",
                "uniqueid": "00:15:8d:00:02:a5:21:24-01-0101",
            },
        },
        AsyncMock(),
    )
    sensor = sensors["0"]

    assert sensor.BINARY is True
    assert sensor.ZHATYPE == ("ZHACarbonMonoxide",)

    assert sensor.state is False
    assert sensor.carbonmonoxide is False

    # DeconzSensor
    assert sensor.battery == 100
    assert sensor.ep == 1
    assert sensor.lowbattery is False
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is False
    assert sensor.secondary_temperature is None

    # DeconzDevice
    assert sensor.deconz_id == "/sensors/0"
    assert sensor.etag == "b7599df551944df97b2aa87d160b9c45"
    assert sensor.manufacturer == "Heiman"
    assert sensor.modelid == "CO_V16"
    assert sensor.name == "Cave, CO"
    assert sensor.swversion == "20150330"
    assert sensor.type == "ZHACarbonMonoxide"
    assert sensor.uniqueid == "00:15:8d:00:02:a5:21:24-01-0101"


async def test_consumption_sensor():
    """Verify that consumption sensor works."""
    sensors = Sensors(
        {
            "0": {
                "config": {"on": True, "reachable": True},
                "ep": 1,
                "etag": "a99e5bc463d15c23af7e89946e784cca",
                "manufacturername": "Heiman",
                "modelid": "SmartPlug",
                "name": "Consumption 15",
                "state": {
                    "consumption": 11342,
                    "lastupdated": "2018-03-12T19:19:08",
                    "power": 123,
                },
                "type": "ZHAConsumption",
                "uniqueid": "00:0d:6f:00:0b:7a:64:29-01-0702",
            },
        },
        AsyncMock(),
    )
    sensor = sensors["0"]

    assert sensor.BINARY is False
    assert sensor.ZHATYPE == ("ZHAConsumption",)

    assert sensor.state == 11.342
    assert sensor.consumption == 11342
    assert sensor.power == 123

    # DeconzSensor
    assert sensor.battery is None
    assert sensor.ep == 1
    assert sensor.lowbattery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.secondary_temperature is None

    # DeconzDevice
    assert sensor.deconz_id == "/sensors/0"
    assert sensor.etag == "a99e5bc463d15c23af7e89946e784cca"
    assert sensor.manufacturer == "Heiman"
    assert sensor.modelid == "SmartPlug"
    assert sensor.name == "Consumption 15"
    assert sensor.swversion is None
    assert sensor.type == "ZHAConsumption"
    assert sensor.uniqueid == "00:0d:6f:00:0b:7a:64:29-01-0702"

    del sensor.raw["state"]["consumption"]
    assert sensor.state is None


async def test_daylight_sensor():
    """Verify that daylight sensor works."""
    sensors = Sensors(
        {
            "0": {
                "config": {
                    "configured": True,
                    "on": True,
                    "sunriseoffset": 30,
                    "sunsetoffset": -30,
                },
                "etag": "55047cf652a7e594d0ee7e6fae01dd38",
                "manufacturername": "Philips",
                "modelid": "PHDL00",
                "name": "Daylight",
                "state": {
                    "daylight": True,
                    "lastupdated": "2018-03-24T17:26:12",
                    "status": 170,
                },
                "swversion": "1.0",
                "type": "Daylight",
            },
        },
        AsyncMock(),
    )
    sensor = sensors["0"]

    assert sensor.BINARY is False
    assert sensor.ZHATYPE == ("Daylight",)

    assert sensor.state == "solar_noon"
    assert sensor.configured is True
    assert sensor.daylight is True
    assert sensor.status == "solar_noon"
    assert sensor.sunriseoffset == 30
    assert sensor.sunsetoffset == -30

    # DeconzSensor
    assert sensor.battery is None
    assert sensor.ep is None
    assert sensor.lowbattery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.secondary_temperature is None

    # DeconzDevice
    assert sensor.deconz_id == "/sensors/0"
    assert sensor.etag == "55047cf652a7e594d0ee7e6fae01dd38"
    assert sensor.manufacturer == "Philips"
    assert sensor.modelid == "PHDL00"
    assert sensor.name == "Daylight"
    assert sensor.swversion == "1.0"
    assert sensor.type == "Daylight"
    assert sensor.uniqueid is None

    statuses = {
        100: "nadir",
        110: "night_end",
        120: "nautical_dawn",
        130: "dawn",
        140: "sunrise_start",
        150: "sunrise_end",
        160: "golden_hour_1",
        170: "solar_noon",
        180: "golden_hour_2",
        190: "sunset_start",
        200: "sunset_end",
        210: "dusk",
        220: "nautical_dusk",
        230: "night_start",
        0: "unknown",
    }

    for k, v in statuses.items():
        event = {"state": {"status": k}}
        sensor.update(event)

        assert sensor.state == v
        assert sensor.changed_keys == {"state", "status"}


async def test_fire_sensor():
    """Verify that fire sensor works."""
    sensors = Sensors(
        {
            "0": {
                "config": {"on": True, "reachable": True},
                "ep": 1,
                "etag": "2b585d2c016bfd665ba27a8fdad28670",
                "manufacturername": "LUMI",
                "modelid": "lumi.sensor_smoke",
                "name": "sensor_kitchen_smoke",
                "state": {"fire": False, "lastupdated": "2018-02-20T11:25:02"},
                "type": "ZHAFire",
                "uniqueid": "00:15:8d:00:01:d9:3e:7c-01-0500",
            },
        },
        AsyncMock(),
    )
    sensor = sensors["0"]

    assert sensor.BINARY is True
    assert sensor.ZHATYPE == ("ZHAFire",)

    assert sensor.state is False
    assert sensor.fire is False

    # DeconzSensor
    assert sensor.battery is None
    assert sensor.ep == 1
    assert sensor.lowbattery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.secondary_temperature is None

    # DeconzDevice
    assert sensor.deconz_id == "/sensors/0"
    assert sensor.etag == "2b585d2c016bfd665ba27a8fdad28670"
    assert sensor.manufacturer == "LUMI"
    assert sensor.modelid == "lumi.sensor_smoke"
    assert sensor.name == "sensor_kitchen_smoke"
    assert sensor.swversion is None
    assert sensor.type == "ZHAFire"
    assert sensor.uniqueid == "00:15:8d:00:01:d9:3e:7c-01-0500"


async def test_genericflag_sensor():
    """Verify that generic flag sensor works."""
    sensors = Sensors(
        {
            "0": {
                "config": {"on": True, "reachable": True},
                "modelid": "Switch",
                "name": "Kitchen Switch",
                "state": {"flag": True, "lastupdated": "2018-07-01T10:40:35"},
                "swversion": "1.0.0",
                "type": "CLIPGenericFlag",
                "uniqueid": "kitchen-switch",
            },
        },
        AsyncMock(),
    )
    sensor = sensors["0"]

    assert sensor.BINARY is True
    assert sensor.ZHATYPE == ("CLIPGenericFlag",)

    assert sensor.state is True
    assert sensor.flag is True

    # DeconzSensor
    assert sensor.battery is None
    assert sensor.ep is None
    assert sensor.lowbattery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.secondary_temperature is None

    # DeconzDevice
    assert sensor.deconz_id == "/sensors/0"
    assert sensor.etag is None
    assert sensor.manufacturer is ""
    assert sensor.modelid == "Switch"
    assert sensor.name == "Kitchen Switch"
    assert sensor.swversion == "1.0.0"
    assert sensor.type == "CLIPGenericFlag"
    assert sensor.uniqueid == "kitchen-switch"


async def test_genericstatus_sensor():
    """Verify that generic flag sensor works."""
    sensors = Sensors(
        {
            "0": {
                "config": {"on": True, "reachable": True},
                "etag": "aacc83bc7d6e4af7e44014e9f776b206",
                "manufacturername": "Phoscon",
                "modelid": "PHOSCON_FSM_STATE",
                "name": "FSM_STATE Motion stair",
                "state": {"lastupdated": "2019-04-24T00:00:25", "status": 0},
                "swversion": "1.0",
                "type": "CLIPGenericStatus",
                "uniqueid": "fsm-state-1520195376277",
            },
        },
        AsyncMock(),
    )
    sensor = sensors["0"]

    assert sensor.BINARY is False
    assert sensor.ZHATYPE == ("CLIPGenericStatus",)

    assert sensor.state == 0
    assert sensor.status == 0

    # DeconzSensor
    assert sensor.battery is None
    assert sensor.ep is None
    assert sensor.lowbattery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.secondary_temperature is None

    # DeconzDevice
    assert sensor.deconz_id == "/sensors/0"
    assert sensor.etag == "aacc83bc7d6e4af7e44014e9f776b206"
    assert sensor.manufacturer == "Phoscon"
    assert sensor.modelid == "PHOSCON_FSM_STATE"
    assert sensor.name == "FSM_STATE Motion stair"
    assert sensor.swversion == "1.0"
    assert sensor.type == "CLIPGenericStatus"
    assert sensor.uniqueid == "fsm-state-1520195376277"


async def test_humidity_sensor():
    """Verify that humidity sensor works."""
    sensors = Sensors(
        {
            "0": {
                "config": {"battery": 100, "offset": 0, "on": True, "reachable": True},
                "ep": 1,
                "etag": "1220e5d026493b6e86207993703a8a71",
                "manufacturername": "LUMI",
                "modelid": "lumi.weather",
                "name": "Mi temperature 1",
                "state": {"humidity": 3555, "lastupdated": "2019-05-05T14:39:00"},
                "swversion": "20161129",
                "type": "ZHAHumidity",
                "uniqueid": "00:15:8d:00:02:45:dc:53-01-0405",
            },
        },
        AsyncMock(),
    )
    sensor = sensors["0"]

    assert sensor.BINARY is False
    assert sensor.ZHATYPE == ("ZHAHumidity", "CLIPHumidity")

    assert sensor.state == 35.5
    assert sensor.humidity == 3555

    # DeconzSensor
    assert sensor.battery == 100
    assert sensor.ep == 1
    assert sensor.lowbattery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.secondary_temperature is None

    # DeconzDevice
    assert sensor.deconz_id == "/sensors/0"
    assert sensor.etag == "1220e5d026493b6e86207993703a8a71"
    assert sensor.manufacturer == "LUMI"
    assert sensor.modelid == "lumi.weather"
    assert sensor.name == "Mi temperature 1"
    assert sensor.swversion == "20161129"
    assert sensor.type == "ZHAHumidity"
    assert sensor.uniqueid == "00:15:8d:00:02:45:dc:53-01-0405"

    del sensor.raw["state"]["humidity"]
    assert sensor.state is None


async def test_lightlevel_sensor():
    """Verify that light level sensor works."""
    sensors = Sensors(
        {
            "0": {
                "config": {
                    "alert": "none",
                    "battery": 100,
                    "ledindication": False,
                    "on": True,
                    "pending": [],
                    "reachable": True,
                    "tholddark": 12000,
                    "tholdoffset": 7000,
                    "usertest": False,
                },
                "ep": 2,
                "etag": "5cfb81765e86aa53ace427cfd52c6d52",
                "manufacturername": "Philips",
                "modelid": "SML001",
                "name": "Motion sensor 4",
                "state": {
                    "dark": True,
                    "daylight": False,
                    "lastupdated": "2019-05-05T14:37:06",
                    "lightlevel": 6955,
                    "lux": 5,
                },
                "swversion": "6.1.0.18912",
                "type": "ZHALightLevel",
                "uniqueid": "00:17:88:01:03:28:8c:9b-02-0400",
            },
        },
        AsyncMock(),
    )
    sensor = sensors["0"]

    assert sensor.BINARY is False
    assert sensor.ZHATYPE == ("ZHALightLevel", "CLIPLightLevel")

    assert sensor.state == 5
    assert sensor.dark is True
    assert sensor.daylight is False
    assert sensor.lightlevel == 6955
    assert sensor.lux == 5
    assert sensor.tholddark == 12000
    assert sensor.tholdoffset == 7000

    # DeconzSensor
    assert sensor.battery == 100
    assert sensor.ep == 2
    assert sensor.lowbattery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.secondary_temperature is None

    # DeconzDevice
    assert sensor.deconz_id == "/sensors/0"
    assert sensor.etag == "5cfb81765e86aa53ace427cfd52c6d52"
    assert sensor.manufacturer == "Philips"
    assert sensor.modelid == "SML001"
    assert sensor.name == "Motion sensor 4"
    assert sensor.swversion == "6.1.0.18912"
    assert sensor.type == "ZHALightLevel"
    assert sensor.uniqueid == "00:17:88:01:03:28:8c:9b-02-0400"

    del sensor.raw["state"]["lightlevel"]
    assert sensor.state is None


async def test_openclose_sensor():
    """Verify that open/close sensor works."""
    sensors = Sensors(
        {
            "0": {
                "config": {
                    "battery": 95,
                    "on": True,
                    "reachable": True,
                    "temperature": 3300,
                },
                "ep": 1,
                "etag": "66cc641d0368110da6882b50090174ac",
                "manufacturername": "LUMI",
                "modelid": "lumi.sensor_magnet.aq2",
                "name": "Back Door",
                "state": {"lastupdated": "2019-05-05T14:54:32", "open": False},
                "swversion": "20161128",
                "type": "ZHAOpenClose",
                "uniqueid": "00:15:8d:00:02:2b:96:b4-01-0006",
            },
        },
        AsyncMock(),
    )
    sensor = sensors["0"]

    assert sensor.BINARY is True
    assert sensor.ZHATYPE == ("ZHAOpenClose", "CLIPOpenClose")

    assert sensor.state is False
    assert sensor.open is False

    # DeconzSensor
    assert sensor.battery == 95
    assert sensor.ep == 1
    assert sensor.lowbattery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.secondary_temperature == 33

    # DeconzDevice
    assert sensor.deconz_id == "/sensors/0"
    assert sensor.etag == "66cc641d0368110da6882b50090174ac"
    assert sensor.manufacturer == "LUMI"
    assert sensor.modelid == "lumi.sensor_magnet.aq2"
    assert sensor.name == "Back Door"
    assert sensor.swversion == "20161128"
    assert sensor.type == "ZHAOpenClose"
    assert sensor.uniqueid == "00:15:8d:00:02:2b:96:b4-01-0006"


async def test_power_sensor():
    """Verify that power sensor works."""
    sensors = Sensors(
        {
            "0": {
                "config": {"on": True, "reachable": True},
                "ep": 1,
                "etag": "96e71c7db4685b334d3d0decc3f11868",
                "manufacturername": "Heiman",
                "modelid": "SmartPlug",
                "name": "Power 16",
                "state": {
                    "current": 34,
                    "lastupdated": "2018-03-12T19:22:13",
                    "power": 64,
                    "voltage": 231,
                },
                "type": "ZHAPower",
                "uniqueid": "00:0d:6f:00:0b:7a:64:29-01-0b04",
            },
        },
        AsyncMock(),
    )
    sensor = sensors["0"]

    assert sensor.BINARY is False
    assert sensor.ZHATYPE == ("ZHAPower",)

    assert sensor.state == 64
    assert sensor.current == 34
    assert sensor.power == 64
    assert sensor.voltage == 231

    # DeconzSensor
    assert sensor.battery is None
    assert sensor.ep == 1
    assert sensor.lowbattery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.secondary_temperature is None

    # DeconzDevice
    assert sensor.deconz_id == "/sensors/0"
    assert sensor.etag == "96e71c7db4685b334d3d0decc3f11868"
    assert sensor.manufacturer == "Heiman"
    assert sensor.modelid == "SmartPlug"
    assert sensor.name == "Power 16"
    assert sensor.swversion is None
    assert sensor.type == "ZHAPower"
    assert sensor.uniqueid == "00:0d:6f:00:0b:7a:64:29-01-0b04"


async def test_presence_sensor():
    """Verify that presence sensor works."""
    sensors = Sensors(
        {
            "0": {
                "config": {
                    "alert": "none",
                    "battery": 100,
                    "delay": 0,
                    "ledindication": False,
                    "on": True,
                    "pending": [],
                    "reachable": True,
                    "sensitivity": 2,
                    "sensitivitymax": 2,
                    "usertest": False,
                },
                "ep": 2,
                "etag": "5cfb81765e86aa53ace427cfd52c6d52",
                "manufacturername": "Philips",
                "modelid": "SML001",
                "name": "Motion sensor 4",
                "state": {"lastupdated": "2019-05-05T14:37:06", "presence": False},
                "swversion": "6.1.0.18912",
                "type": "ZHAPresence",
                "uniqueid": "00:17:88:01:03:28:8c:9b-02-0406",
            },
        },
        AsyncMock(),
    )
    sensor = sensors["0"]

    assert sensor.BINARY is True
    assert sensor.ZHATYPE == ("ZHAPresence", "CLIPPresence")

    assert sensor.state is False
    assert sensor.presence is False
    assert sensor.dark is None
    assert sensor.duration is None

    # DeconzSensor
    assert sensor.battery == 100
    assert sensor.ep == 2
    assert sensor.lowbattery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.secondary_temperature is None

    # DeconzDevice
    assert sensor.deconz_id == "/sensors/0"
    assert sensor.etag == "5cfb81765e86aa53ace427cfd52c6d52"
    assert sensor.manufacturer == "Philips"
    assert sensor.modelid == "SML001"
    assert sensor.name == "Motion sensor 4"
    assert sensor.swversion == "6.1.0.18912"
    assert sensor.type == "ZHAPresence"
    assert sensor.uniqueid == "00:17:88:01:03:28:8c:9b-02-0406"


async def test_pressure_sensor():
    """Verify that pressure sensor works."""
    sensors = Sensors(
        {
            "0": {
                "config": {"battery": 100, "on": True, "reachable": True},
                "ep": 1,
                "etag": "1220e5d026493b6e86207993703a8a71",
                "manufacturername": "LUMI",
                "modelid": "lumi.weather",
                "name": "Mi temperature 1",
                "state": {"lastupdated": "2019-05-05T14:39:00", "pressure": 1010},
                "swversion": "20161129",
                "type": "ZHAPressure",
                "uniqueid": "00:15:8d:00:02:45:dc:53-01-0403",
            },
        },
        AsyncMock(),
    )
    sensor = sensors["0"]

    assert sensor.BINARY is False
    assert sensor.ZHATYPE == ("ZHAPressure", "CLIPPressure")

    assert sensor.state == 1010
    assert sensor.pressure == 1010

    # DeconzSensor
    assert sensor.battery == 100
    assert sensor.ep == 1
    assert sensor.lowbattery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.secondary_temperature is None

    # DeconzDevice
    assert sensor.deconz_id == "/sensors/0"
    assert sensor.etag == "1220e5d026493b6e86207993703a8a71"
    assert sensor.manufacturer == "LUMI"
    assert sensor.modelid == "lumi.weather"
    assert sensor.name == "Mi temperature 1"
    assert sensor.swversion == "20161129"
    assert sensor.type == "ZHAPressure"
    assert sensor.uniqueid == "00:15:8d:00:02:45:dc:53-01-0403"


async def test_switch_sensor():
    """Verify that switch sensor works."""
    sensors = Sensors(
        {
            "0": {
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
                "state": {"buttonevent": 1002, "lastupdated": "2019-04-28T20:29:13"},
                "swversion": "5.45.1.17846",
                "type": "ZHASwitch",
                "uniqueid": "00:17:88:01:02:0e:32:a3-02-fc00",
            },
        },
        AsyncMock(),
    )
    sensor = sensors["0"]

    assert sensor.BINARY is False
    assert sensor.ZHATYPE == ("ZHASwitch", "ZGPSwitch", "CLIPSwitch")

    assert sensor.state == 1002
    assert sensor.buttonevent == 1002
    assert sensor.gesture is None
    assert sensor.angle is None
    assert sensor.xy is None

    # DeconzSensor
    assert sensor.battery == 90
    assert sensor.ep == 2
    assert sensor.lowbattery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.secondary_temperature is None

    # DeconzDevice
    assert sensor.deconz_id == "/sensors/0"
    assert sensor.etag == "233ae541bbb7ac98c42977753884b8d2"
    assert sensor.manufacturer == "Philips"
    assert sensor.modelid == "RWL021"
    assert sensor.name == "Dimmer switch 3"
    assert sensor.swversion == "5.45.1.17846"
    assert sensor.type == "ZHASwitch"
    assert sensor.uniqueid == "00:17:88:01:02:0e:32:a3-02-fc00"


async def test_switch_sensor_cube():
    """Verify that cube switch sensor works."""
    sensors = Sensors(
        {
            "0": {
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
            },
        },
        AsyncMock(),
    )
    sensor = sensors["0"]

    assert sensor.BINARY is False
    assert sensor.ZHATYPE == ("ZHASwitch", "ZGPSwitch", "CLIPSwitch")

    assert sensor.state == 747
    assert sensor.buttonevent == 747
    assert sensor.gesture == 7

    # DeconzSensor
    assert sensor.battery == 90
    assert sensor.ep == 3
    assert sensor.lowbattery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.secondary_temperature == 11.0

    # DeconzDevice
    assert sensor.deconz_id == "/sensors/0"
    assert sensor.etag == "e34fa1c7a19d960e35a1f4d56ac475af"
    assert sensor.manufacturer == "LUMI"
    assert sensor.modelid == "lumi.sensor_cube.aqgl01"
    assert sensor.name == "Mi Magic Cube"
    assert sensor.swversion == "20160704"
    assert sensor.type == "ZHASwitch"
    assert sensor.uniqueid == "00:15:8d:00:02:8b:3b:24-03-000c"


async def test_switch_sensor_tint_remote():
    """Verify that tint remote sensor works."""
    sensors = Sensors(
        {
            "0": {
                "config": {"group": "16388,16389,16390", "on": True, "reachable": True},
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
            },
        },
        AsyncMock(),
    )
    sensor = sensors["0"]

    assert sensor.BINARY is False
    assert sensor.ZHATYPE == ("ZHASwitch", "ZGPSwitch", "CLIPSwitch")

    assert sensor.state == 6002
    assert sensor.buttonevent == 6002
    assert sensor.angle == 10
    assert sensor.xy == [0.3381, 0.1627]

    # DeconzSensor
    assert sensor.ep == 1
    assert sensor.lowbattery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None

    # DeconzDevice
    assert sensor.deconz_id == "/sensors/0"
    assert sensor.etag == "b1336f750d31300afa441a04f2c69b68"
    assert sensor.manufacturer == "MLI"
    assert sensor.modelid == "ZBT-Remote-ALL-RGBW"
    assert sensor.name == "ZHA Remote 1"
    assert sensor.swversion == "2.0"
    assert sensor.type == "ZHASwitch"
    assert sensor.uniqueid == "00:11:22:33:44:55:66:77-01-1000"


async def test_switch_ubisys_j1():
    """Verify that tint remote sensor works."""
    sensors = Sensors(
        {
            "0": {
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
                "state": {"buttonevent": None, "lastupdated": "none"},
                "swversion": "20190129-DE-FB0",
                "type": "ZHASwitch",
                "uniqueid": "00:1f:ee:00:00:00:00:09-02-0102",
            },
        },
        AsyncMock(),
    )
    sensor = sensors["0"]

    assert sensor.BINARY is False
    assert sensor.ZHATYPE == ("ZHASwitch", "ZGPSwitch", "CLIPSwitch")

    assert sensor.state is None
    assert sensor.buttonevent is None
    assert sensor.angle is None
    assert sensor.xy is None
    assert sensor.mode == "momentary"
    assert sensor.windowcoveringtype == 0

    # DeconzSensor
    assert sensor.ep == 2
    assert sensor.lowbattery is None
    assert sensor.on is True
    assert sensor.reachable is False
    assert sensor.tampered is None

    # DeconzDevice
    assert sensor.deconz_id == "/sensors/0"
    assert sensor.etag == "da5fbb89eca4133b6949537e73b31f77"
    assert sensor.manufacturer == "ubisys"
    assert sensor.modelid == "J1 (5502)"
    assert sensor.name == "J1"
    assert sensor.swversion == "20190129-DE-FB0"
    assert sensor.type == "ZHASwitch"
    assert sensor.uniqueid == "00:1f:ee:00:00:00:00:09-02-0102"


async def test_temperature_sensor():
    """Verify that temperature sensor works."""
    sensors = Sensors(
        {
            "0": {
                "config": {"battery": 100, "offset": 0, "on": True, "reachable": True},
                "ep": 1,
                "etag": "1220e5d026493b6e86207993703a8a71",
                "manufacturername": "LUMI",
                "modelid": "lumi.weather",
                "name": "Mi temperature 1",
                "state": {"lastupdated": "2019-05-05T14:39:00", "temperature": 2182},
                "swversion": "20161129",
                "type": "ZHATemperature",
                "uniqueid": "00:15:8d:00:02:45:dc:53-01-0402",
            },
        },
        AsyncMock(),
    )
    sensor = sensors["0"]

    assert sensor.BINARY is False
    assert sensor.ZHATYPE == ("ZHATemperature", "CLIPTemperature")

    assert sensor.state == 21.8
    assert sensor.temperature == 21.8

    # DeconzSensor
    assert sensor.battery == 100
    assert sensor.ep == 1
    assert sensor.lowbattery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.secondary_temperature is None

    # DeconzDevice
    assert sensor.deconz_id == "/sensors/0"
    assert sensor.etag == "1220e5d026493b6e86207993703a8a71"
    assert sensor.manufacturer == "LUMI"
    assert sensor.modelid == "lumi.weather"
    assert sensor.name == "Mi temperature 1"
    assert sensor.swversion == "20161129"
    assert sensor.type == "ZHATemperature"
    assert sensor.uniqueid == "00:15:8d:00:02:45:dc:53-01-0402"

    del sensor.raw["state"]["temperature"]
    assert sensor.state is None


async def test_thermostat_sensor():
    """Verify that thermostat sensor works."""
    sensors = Sensors(
        {
            "0": {
                "config": {
                    "battery": 100,
                    "displayflipped": True,
                    "heatsetpoint": 2100,
                    "locked": False,
                    "mode": "auto",
                    "offset": 0,
                    "on": True,
                    "reachable": True,
                },
                "ep": 1,
                "etag": "25aac331bc3c4b465cfb2197f6243ea4",
                "manufacturername": "Eurotronic",
                "modelid": "SPZB0001",
                "name": "Living Room Radiator",
                "state": {
                    "lastupdated": "2019-02-10T22:41:32",
                    "on": False,
                    "temperature": 2149,
                    "valve": 0,
                },
                "swversion": "15181120",
                "type": "ZHAThermostat",
                "uniqueid": "00:15:8d:00:01:92:d2:51-01-0201",
            },
        },
        AsyncMock(),
    )
    sensor = sensors["0"]

    assert sensor.BINARY is False
    assert sensor.ZHATYPE == ("ZHAThermostat", "CLIPThermostat")

    assert sensor.state == 21.5
    assert sensor.coolsetpoint is None
    assert sensor.errorcode is None
    assert sensor.fanmode is None
    assert sensor.floortemperature is None
    assert sensor.heating is None
    assert sensor.heatsetpoint == 21.00
    assert sensor.locked is False
    assert sensor.mode == "auto"
    assert sensor.mountingmode is None
    assert sensor.mountingmodeactive is None
    assert sensor.offset == 0
    assert sensor.preset is None
    assert sensor.state_on is False
    assert sensor.swingmode is None
    assert sensor.temperature == 21.5
    assert sensor.temperaturemeasurement is None
    assert sensor.valve == 0
    assert sensor.windowopen_set is None

    # DeconzSensor
    assert sensor.battery == 100
    assert sensor.ep == 1
    assert sensor.lowbattery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.secondary_temperature is None

    # DeconzDevice
    assert sensor.deconz_id == "/sensors/0"
    assert sensor.etag == "25aac331bc3c4b465cfb2197f6243ea4"
    assert sensor.manufacturer == "Eurotronic"
    assert sensor.modelid == "SPZB0001"
    assert sensor.name == "Living Room Radiator"
    assert sensor.swversion == "15181120"
    assert sensor.type == "ZHAThermostat"
    assert sensor.uniqueid == "00:15:8d:00:01:92:d2:51-01-0201"


async def test_tuya_thermostat_sensor():
    """Verify that Tuya thermostat works."""
    sensors = Sensors(
        {
            "0": {
                "config": {
                    "battery": 100,
                    "heatsetpoint": 1550,
                    "locked": None,
                    "offset": 0,
                    "on": True,
                    "preset": "auto",
                    "reachable": True,
                    "schedule": {},
                    "schedule_on": None,
                    "setvalve": True,
                    "windowopen_set": True,
                },
                "ep": 1,
                "etag": "36850fc8521f7c23606c9304b2e1f7bb",
                "lastseen": "2020-11-11T21:23Z",
                "manufacturername": "_TYST11_kfvq6avy",
                "modelid": "fvq6avy",
                "name": "fvq6avy",
                "state": {"lastupdated": "none", "on": None, "temperature": 2290},
                "swversion": "20180727",
                "type": "ZHAThermostat",
                "uniqueid": "bc:33:ac:ff:fe:47:a1:95-01-0201",
            },
        },
        AsyncMock(),
    )
    sensor = sensors["0"]

    assert sensor.BINARY is False
    assert sensor.ZHATYPE == Thermostat.ZHATYPE

    assert sensor.state == 22.9
    assert sensor.heatsetpoint == 15.50
    assert sensor.locked is None
    assert sensor.mode is None
    assert sensor.offset == 0
    assert sensor.state_on is None
    assert sensor.temperature == 22.9
    assert sensor.valve is None

    # DeconzSensor
    assert sensor.battery == 100
    assert sensor.ep == 1
    assert sensor.lowbattery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.secondary_temperature is None

    # DeconzDevice
    assert sensor.deconz_id == "/sensors/0"
    assert sensor.etag == "36850fc8521f7c23606c9304b2e1f7bb"
    assert sensor.manufacturer == "_TYST11_kfvq6avy"
    assert sensor.modelid == "fvq6avy"
    assert sensor.name == "fvq6avy"
    assert sensor.swversion == "20180727"
    assert sensor.type == "ZHAThermostat"
    assert sensor.uniqueid == "bc:33:ac:ff:fe:47:a1:95-01-0201"


async def test_time_sensor():
    """Verify that time sensor works."""
    sensors = Sensors(
        {
            "0": {
                "config": {"battery": 40, "on": True, "reachable": True},
                "ep": 1,
                "etag": "28e796678d9a24712feef59294343bb6",
                "lastseen": "2020-11-22T11:26Z",
                "manufacturername": "Danfoss",
                "modelid": "eTRV0100",
                "name": "eTRV Séjour",
                "state": {
                    "lastset": "2020-11-19T08:07:08Z",
                    "lastupdated": "2020-11-22T10:51:03.444",
                    "localtime": "2020-11-22T10:51:01",
                    "utc": "2020-11-22T10:51:01Z",
                },
                "swversion": "20200429",
                "type": "ZHATime",
                "uniqueid": "cc:cc:cc:ff:fe:38:4d:b3-01-000a",
            },
        },
        AsyncMock(),
    )
    sensor = sensors["0"]

    assert sensor.BINARY is False
    assert sensor.ZHATYPE == ("ZHATime",)

    assert sensor.state == "2020-11-19T08:07:08Z"
    assert sensor.lastset == "2020-11-19T08:07:08Z"

    # DeconzSensor
    assert sensor.battery == 40
    assert sensor.ep == 1
    assert sensor.lowbattery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.secondary_temperature is None

    # DeconzDevice
    assert sensor.deconz_id == "/sensors/0"
    assert sensor.etag == "28e796678d9a24712feef59294343bb6"
    assert sensor.manufacturer == "Danfoss"
    assert sensor.modelid == "eTRV0100"
    assert sensor.name == "eTRV Séjour"
    assert sensor.swversion == "20200429"
    assert sensor.type == "ZHATime"
    assert sensor.uniqueid == "cc:cc:cc:ff:fe:38:4d:b3-01-000a"


async def test_vibration_sensor():
    """Verify that vibration sensor works."""
    sensors = Sensors(
        {
            "0": {
                "config": {
                    "battery": 91,
                    "on": True,
                    "pending": [],
                    "reachable": True,
                    "sensitivity": 21,
                    "sensitivitymax": 21,
                    "temperature": 3200,
                },
                "ep": 1,
                "etag": "b7599df551944df97b2aa87d160b9c45",
                "manufacturername": "LUMI",
                "modelid": "lumi.vibration.aq1",
                "name": "Vibration 1",
                "state": {
                    "lastupdated": "2019-03-09T15:53:07",
                    "orientation": [10, 1059, 0],
                    "tiltangle": 83,
                    "vibration": True,
                    "vibrationstrength": 114,
                },
                "swversion": "20180130",
                "type": "ZHAVibration",
                "uniqueid": "00:15:8d:00:02:a5:21:24-01-0101",
            },
        },
        AsyncMock(),
    )
    sensor = sensors["0"]

    assert sensor.BINARY is True
    assert sensor.ZHATYPE == ("ZHAVibration",)

    assert sensor.state is True
    assert sensor.orientation == [10, 1059, 0]
    assert sensor.sensitivity == 21
    assert sensor.sensitivitymax == 21
    assert sensor.tiltangle == 83
    assert sensor.vibration is True
    assert sensor.vibrationstrength == 114

    # DeconzSensor
    assert sensor.battery == 91
    assert sensor.ep == 1
    assert sensor.lowbattery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.secondary_temperature == 32

    # DeconzDevice
    assert sensor.deconz_id == "/sensors/0"
    assert sensor.etag == "b7599df551944df97b2aa87d160b9c45"
    assert sensor.manufacturer == "LUMI"
    assert sensor.modelid == "lumi.vibration.aq1"
    assert sensor.name == "Vibration 1"
    assert sensor.swversion == "20180130"
    assert sensor.type == "ZHAVibration"
    assert sensor.uniqueid == "00:15:8d:00:02:a5:21:24-01-0101"

    mock_callback = Mock()
    sensor.register_callback(mock_callback)
    assert sensor._callbacks

    event = {"state": {"lastupdated": "2019-03-15T10:15:17", "orientation": [0, 84, 6]}}
    sensor.update(event)

    mock_callback.assert_called_once()
    assert sensor.changed_keys == {"state", "lastupdated", "orientation"}

    sensor.remove_callback(mock_callback)
    assert not sensor._callbacks


async def test_water_sensor():
    """Verify that water sensor works."""
    sensors = Sensors(
        {
            "0": {
                "config": {
                    "battery": 100,
                    "on": True,
                    "reachable": True,
                    "temperature": 2500,
                },
                "ep": 1,
                "etag": "fae893708dfe9b358df59107d944fa1c",
                "manufacturername": "LUMI",
                "modelid": "lumi.sensor_wleak.aq1",
                "name": "water2",
                "state": {
                    "lastupdated": "2019-01-29T07:13:20",
                    "lowbattery": False,
                    "tampered": False,
                    "water": False,
                },
                "swversion": "20170721",
                "type": "ZHAWater",
                "uniqueid": "00:15:8d:00:02:2f:07:db-01-0500",
            },
        },
        AsyncMock(),
    )
    sensor = sensors["0"]

    assert sensor.BINARY is True
    assert sensor.ZHATYPE == ("ZHAWater",)

    assert sensor.state is False
    assert sensor.water is False

    # DeconzSensor
    assert sensor.battery == 100
    assert sensor.ep == 1
    assert sensor.lowbattery is False
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is False
    assert sensor.secondary_temperature == 25

    # DeconzDevice
    assert sensor.deconz_id == "/sensors/0"
    assert sensor.etag == "fae893708dfe9b358df59107d944fa1c"
    assert sensor.manufacturer == "LUMI"
    assert sensor.modelid == "lumi.sensor_wleak.aq1"
    assert sensor.name == "water2"
    assert sensor.swversion == "20170721"
    assert sensor.type == "ZHAWater"
    assert sensor.uniqueid == "00:15:8d:00:02:2f:07:db-01-0500"
