"""Test pydeCONZ thermostat.

pytest --cov-report term-missing --cov=pydeconz.interfaces.sensors --cov=pydeconz.models.sensor.thermostat tests/sensors/test_thermostat.py
"""

import pytest

from pydeconz.models.sensor.thermostat import (
    ThermostatFanMode,
    ThermostatMode,
    ThermostatPreset,
    ThermostatSwingMode,
    ThermostatTemperatureMeasurement,
)

DATA = {
    "config": {
        "battery": 59,
        "displayflipped": None,
        "heatsetpoint": 2100,
        "locked": None,
        "mountingmode": None,
        "offset": 0,
        "on": True,
        "reachable": True,
    },
    "ep": 1,
    "etag": "6130553ac247174809bae47144ee23f8",
    "lastseen": "2020-11-29T19:31Z",
    "manufacturername": "Danfoss",
    "modelid": "eTRV0100",
    "name": "Thermostat_stue_sofa",
    "state": {
        "errorcode": None,
        "lastupdated": "2020-11-29T19:28:40.665",
        "mountingmodeactive": False,
        "on": True,
        "temperature": 2102,
        "valve": 24,
        "windowopen": "Closed",
    },
    "swversion": "01.02.0008 01.02",
    "type": "ZHAThermostat",
    "uniqueid": "14:b4:57:ff:fe:d5:4e:77-01-0201",
}

DATA_EUROTRONIC = {
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
}
DATA_TUYA = {
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
    "state": {
        "lastupdated": "none",
        "on": None,
        "temperature": 2290,
    },
    "swversion": "20180727",
    "type": "ZHAThermostat",
    "uniqueid": "bc:33:ac:ff:fe:47:a1:95-01-0201",
}


async def test_handler_thermostat(mock_aioresponse, deconz_session, deconz_called_with):
    """Verify that configuring thermostat sensor works."""
    thermostat = deconz_session.sensors.thermostat

    mock_aioresponse.put("http://host:80/api/apikey/sensors/0/config")
    await thermostat.set_config(
        id="0",
        cooling_setpoint=1000,
        enable_schedule=True,
        external_sensor_temperature=24,
        external_window_open=True,
        fan_mode=ThermostatFanMode.AUTO,
        flip_display=False,
        heating_setpoint=500,
        locked=True,
        mode=ThermostatMode.AUTO,
        mounting_mode=False,
        on=True,
        preset=ThermostatPreset.AUTO,
        schedule=[],
        set_valve=True,
        swing_mode=ThermostatSwingMode.HALF_OPEN,
        temperature_measurement=ThermostatTemperatureMeasurement.FLOOR_SENSOR,
        window_open_detection=True,
    )
    assert deconz_called_with(
        "put",
        path="/sensors/0/config",
        json={
            "coolsetpoint": 1000,
            "schedule_on": True,
            "externalsensortemp": 24,
            "externalwindowopen": True,
            "fanmode": "auto",
            "displayflipped": False,
            "heatsetpoint": 500,
            "locked": True,
            "mode": "auto",
            "mountingmode": False,
            "on": True,
            "preset": "auto",
            "schedule": [],
            "setvalve": True,
            "swingmode": "half open",
            "temperaturemeasurement": "floor sensor",
            "windowopen_set": True,
        },
    )


async def test_sensor_danfoss_thermostat(deconz_sensor):
    """Verify that Danfoss thermostat works.

    Danfoss thermostat is the simplest kind with only control over temperaturdeconz_sensore.
    """
    sensor = await deconz_sensor(DATA)

    assert sensor.cooling_setpoint is None
    assert sensor.display_flipped is None
    assert sensor.error_code is None
    assert sensor.external_sensor_temperature is None
    assert sensor.external_window_open is None
    assert sensor.fan_mode is None
    assert sensor.floor_temperature is None
    assert sensor.heating is None
    assert sensor.heating_setpoint == 2100
    assert sensor.scaled_heating_setpoint == 21.00
    assert sensor.locked is None
    assert sensor.mode is None
    assert sensor.mounting_mode is None
    assert sensor.mounting_mode_active is False
    assert sensor.offset == 0
    assert sensor.preset is None
    assert sensor.state_on
    assert sensor.swing_mode is None
    assert sensor.temperature == 2102
    assert sensor.scaled_temperature == 21.0
    assert sensor.temperature_measurement is None
    assert sensor.valve == 24
    assert sensor.window_open_detection is None

    # DeconzSensor
    assert sensor.battery == 59
    assert sensor.ep == 1
    assert sensor.low_battery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.internal_temperature is None

    # DeconzDevice
    assert sensor.deconz_id == "/sensors/0"
    assert sensor.etag == "6130553ac247174809bae47144ee23f8"
    assert sensor.manufacturer == "Danfoss"
    assert sensor.model_id == "eTRV0100"
    assert sensor.name == "Thermostat_stue_sofa"
    assert sensor.software_version == "01.02.0008 01.02"
    assert sensor.type == "ZHAThermostat"
    assert sensor.unique_id == "14:b4:57:ff:fe:d5:4e:77-01-0201"


async def test_sensor_eurotronic_thermostat(deconz_sensor):
    """Verify that thermostat sensor works."""
    sensor = await deconz_sensor(DATA_EUROTRONIC)

    assert sensor.cooling_setpoint is None
    assert sensor.error_code is None
    assert sensor.fan_mode is None
    assert sensor.floor_temperature is None
    assert sensor.heating is None
    assert sensor.heating_setpoint == 2100
    assert sensor.scaled_heating_setpoint == 21.00
    assert sensor.locked is False
    assert sensor.mode == ThermostatMode.AUTO
    assert sensor.mounting_mode is None
    assert sensor.mounting_mode_active is None
    assert sensor.offset == 0
    assert sensor.preset is None
    assert not sensor.state_on
    assert sensor.swing_mode is None
    assert sensor.temperature == 2149
    assert sensor.scaled_temperature == 21.5
    assert sensor.temperature_measurement is None
    assert sensor.valve == 0
    assert sensor.window_open_detection is None

    # DeconzSensor
    assert sensor.battery == 100
    assert sensor.ep == 1
    assert sensor.low_battery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.internal_temperature is None

    # DeconzDevice
    assert sensor.deconz_id == "/sensors/0"
    assert sensor.etag == "25aac331bc3c4b465cfb2197f6243ea4"
    assert sensor.manufacturer == "Eurotronic"
    assert sensor.model_id == "SPZB0001"
    assert sensor.name == "Living Room Radiator"
    assert sensor.software_version == "15181120"
    assert sensor.type == "ZHAThermostat"
    assert sensor.unique_id == "00:15:8d:00:01:92:d2:51-01-0201"


async def test_sensor_tuya_thermostat(deconz_sensor):
    """Verify that Tuya thermostat works."""
    sensor = await deconz_sensor(DATA_TUYA)

    assert sensor.heating_setpoint == 1550
    assert sensor.scaled_heating_setpoint == 15.50
    assert sensor.locked is None
    assert sensor.mode is None
    assert sensor.offset == 0
    assert sensor.schedule_enabled is None
    assert not sensor.state_on
    assert sensor.temperature == 2290
    assert sensor.scaled_temperature == 22.9
    assert sensor.valve is None

    # DeconzSensor
    assert sensor.battery == 100
    assert sensor.ep == 1
    assert sensor.low_battery is None
    assert sensor.on is True
    assert sensor.reachable is True
    assert sensor.tampered is None
    assert sensor.internal_temperature is None

    # DeconzDevice
    assert sensor.deconz_id == "/sensors/0"
    assert sensor.etag == "36850fc8521f7c23606c9304b2e1f7bb"
    assert sensor.manufacturer == "_TYST11_kfvq6avy"
    assert sensor.model_id == "fvq6avy"
    assert sensor.name == "fvq6avy"
    assert sensor.software_version == "20180727"
    assert sensor.type == "ZHAThermostat"
    assert sensor.unique_id == "bc:33:ac:ff:fe:47:a1:95-01-0201"

    # Verify temperature conversion to increase coverage
    sensor.update(
        {
            "config": {
                "coolsetpoint": 1000,
                "externalsensortemp": 2000,
                "heatsetpoint": None,
            },
            "state": {
                "floortemperature": 4000,
            },
        }
    )
    assert sensor.cooling_setpoint == 1000
    assert sensor.scaled_cooling_setpoint == 10
    assert sensor.external_sensor_temperature == 2000
    assert sensor.scaled_external_sensor_temperature == 20
    assert sensor.heating_setpoint is None
    assert sensor.scaled_heating_setpoint is None
    assert sensor.floor_temperature == 4000
    assert sensor.scaled_floor_temperature == 40


PROPERTY_DATA = [
    (
        ("config", "displayflipped"),
        "display_flipped",
        {True: True, False: False, None: None},
    ),
    (
        ("state", "errorcode"),
        "error_code",
        {True: True, False: False, None: None},
    ),
    (
        ("config", "externalwindowopen"),
        "external_window_open",
        {True: True, False: False, None: None},
    ),
    (
        ("state", "heating"),
        "heating",
        {True: True, False: False, None: None},
    ),
    (
        ("config", "locked"),
        "locked",
        {True: True, False: False, None: None},
    ),
    (
        ("state", "mountingmodeactive"),
        "mounting_mode_active",
        {True: True, False: False, None: None},
    ),
    (
        ("config", "offset"),
        "offset",
        {1: 1, 0: 0, None: None},
    ),
    (
        ("config", "schedule_on"),
        "schedule_enabled",
        {True: True, False: False, None: None},
    ),
    (
        ("state", "valve"),
        "valve",
        {1: 1, 0: 0, None: None},
    ),
    (
        ("config", "windowopen_set"),
        "window_open_detection",
        {True: True, False: False, None: None},
    ),
]


@pytest.mark.parametrize("path, property, data", PROPERTY_DATA)
async def test_thermostat_properties(deconz_sensor, path, property, data):
    """Verify normal thermostat properties."""
    sensor = await deconz_sensor({"config": {}, "state": {}, "type": "ZHAThermostat"})

    for input, output in data.items():
        sensor.update({path[0]: {path[1]: input}})
        assert getattr(sensor, property) == output


ENUM_PROPERTY_DATA = [
    (
        ("config", "fanmode"),
        "fan_mode",
        {
            "auto": ThermostatFanMode.AUTO,
            "unsupported": ThermostatFanMode.UNKNOWN,
            None: ThermostatFanMode.UNKNOWN,
        },
    ),
    (
        ("config", "mode"),
        "mode",
        {
            "auto": ThermostatMode.AUTO,
            "unsupported": ThermostatMode.UNKNOWN,
            None: ThermostatMode.UNKNOWN,
        },
    ),
    (
        ("config", "preset"),
        "preset",
        {
            "auto": ThermostatPreset.AUTO,
            "unsupported": ThermostatPreset.UNKNOWN,
            None: ThermostatPreset.UNKNOWN,
        },
    ),
    (
        ("config", "swingmode"),
        "swing_mode",
        {
            "fully open": ThermostatSwingMode.FULLY_OPEN,
            "unsupported": ThermostatSwingMode.UNKNOWN,
            None: ThermostatSwingMode.UNKNOWN,
        },
    ),
    (
        ("config", "temperaturemeasurement"),
        "temperature_measurement",
        {
            "air sensor": ThermostatTemperatureMeasurement.AIR_SENSOR,
            "unsupported": ThermostatTemperatureMeasurement.UNKNOWN,
            None: ThermostatTemperatureMeasurement.UNKNOWN,
        },
    ),
]


@pytest.mark.parametrize("path, property, data", ENUM_PROPERTY_DATA)
async def test_enum_thermostat_properties(deconz_sensor, path, property, data):
    """Verify enum properties return expected values or None."""
    sensor = await deconz_sensor({"config": {}, "state": {}, "type": "ZHAThermostat"})

    assert getattr(sensor, property) is None

    for input, output in data.items():
        sensor.update({path[0]: {path[1]: input}})
        assert getattr(sensor, property) == output


SCALED_PROPERTY_DATA = [
    (
        ("config", "coolsetpoint"),
        "cooling_setpoint",
        {1000: (1000, 10), 0: (0, None), None: (None, None)},
    ),
    (
        ("config", "externalsensortemp"),
        "external_sensor_temperature",
        {2000: (2000, 20), 0: (0, None), None: (None, None)},
    ),
    (
        ("state", "floortemperature"),
        "floor_temperature",
        {3000: (3000, 30), 0: (0, None), None: (None, None)},
    ),
    (
        ("config", "heatsetpoint"),
        "heating_setpoint",
        {4000: (4000, 40), 0: (0, None), None: (None, None)},
    ),
    (
        ("state", "temperature"),
        "temperature",
        {5000: (5000, 50), 0: (0, 0.0)},
    ),
]


@pytest.mark.parametrize("path, property, data", SCALED_PROPERTY_DATA)
async def test_scaled_thermostat_properties(deconz_sensor, path, property, data):
    """Verify the scaling properties of thermostat."""
    sensor = await deconz_sensor({"config": {}, "state": {}, "type": "ZHAThermostat"})

    for input, output in data.items():
        sensor.update({path[0]: {path[1]: input}})
        assert getattr(sensor, property) == output[0]
        assert getattr(sensor, f"scaled_{property}") == output[1]
