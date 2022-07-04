"""Test pydeCONZ sensors.

pytest --cov-report term-missing --cov=pydeconz.sensor tests/test_sensors.py
"""

from tests import sensors as sensor_test_data


async def test_create_all_sensors(deconz_refresh_state):
    """Verify that creating all sensors work."""
    deconz_session = await deconz_refresh_state(
        sensors={
            "0": sensor_test_data.test_air_purifier.DATA,
            "1": sensor_test_data.test_air_quality.DATA,
            "2": sensor_test_data.test_alarm.DATA,
            "3": sensor_test_data.test_ancillary_control.DATA,
            "4": sensor_test_data.test_battery.DATA,
            "5": sensor_test_data.test_carbon_monoxide.DATA,
            "6": sensor_test_data.test_consumption.DATA,
            "7": sensor_test_data.test_daylight.DATA,
            "8": sensor_test_data.test_door_lock.DATA,
            "9": sensor_test_data.test_fire.DATA,
            "10": sensor_test_data.test_generic_flag.DATA,
            "11": sensor_test_data.test_generic_status.DATA,
            "12": sensor_test_data.test_humidity.DATA,
            "13": sensor_test_data.test_light_level.DATA,
            "14": sensor_test_data.test_open_close.DATA,
            "15": sensor_test_data.test_power.DATA,
            "16": sensor_test_data.test_presence.DATA,
            "17": sensor_test_data.test_pressure.DATA,
            "18": sensor_test_data.test_relative_rotary.DATA,
            "19": sensor_test_data.test_switch.DATA,
            "20": sensor_test_data.test_temperature.DATA,
            "21": sensor_test_data.test_thermostat.DATA,
            "22": sensor_test_data.test_time.DATA,
            "23": sensor_test_data.test_vibration.DATA,
            "24": sensor_test_data.test_water.DATA,
        },
    )
    sensors = deconz_session.sensors
    assert len(sensors._handlers) == 25
    assert sensors["0"].type == "ZHAAirPurifier"
    assert sensors["1"].type == "ZHAAirQuality"
    assert sensors["2"].type == "ZHAAlarm"
    assert sensors["3"].type == "ZHAAncillaryControl"
    assert sensors["4"].type == "ZHABattery"
    assert sensors["5"].type == "ZHACarbonMonoxide"
    assert sensors["6"].type == "ZHAConsumption"
    assert sensors["7"].type == "Daylight"
    assert sensors["8"].type == "ZHADoorLock"
    assert sensors["9"].type == "ZHAFire"
    assert sensors["10"].type == "CLIPGenericFlag"
    assert sensors["11"].type == "CLIPGenericStatus"
    assert sensors["12"].type == "ZHAHumidity"
    assert sensors["13"].type == "ZHALightLevel"
    assert sensors["14"].type == "ZHAOpenClose"
    assert sensors["15"].type == "ZHAPower"
    assert sensors["16"].type == "ZHAPresence"
    assert sensors["17"].type == "ZHAPressure"
    assert sensors["18"].type == "ZHARelativeRotary"
    assert sensors["19"].type == "ZHASwitch"
    assert sensors["20"].type == "ZHATemperature"
    assert sensors["21"].type == "ZHAThermostat"
    assert sensors["22"].type == "ZHATime"
    assert sensors["23"].type == "ZHAVibration"
    assert sensors["24"].type == "ZHAWater"
