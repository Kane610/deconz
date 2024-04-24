"""Test pydeCONZ sensors.

pytest --cov-report term-missing --cov=pydeconz.sensor tests/test_sensors.py
"""

from pydeconz.models import ResourceType

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
            "5": sensor_test_data.test_carbon_dioxide.DATA,
            "6": sensor_test_data.test_carbon_monoxide.DATA,
            "7": sensor_test_data.test_consumption.DATA,
            "8": sensor_test_data.test_daylight.DATA,
            "9": sensor_test_data.test_door_lock.DATA,
            "10": sensor_test_data.test_fire.DATA,
            "11": sensor_test_data.test_formaldehyde.DATA,
            "12": sensor_test_data.test_generic_flag.DATA,
            "13": sensor_test_data.test_generic_status.DATA,
            "14": sensor_test_data.test_humidity.DATA,
            "15": sensor_test_data.test_light_level.DATA,
            "16": sensor_test_data.test_moisture.DATA,
            "17": sensor_test_data.test_open_close.DATA,
            "18": sensor_test_data.test_particulate_matter.DATA,
            "19": sensor_test_data.test_power.DATA,
            "20": sensor_test_data.test_presence.DATA,
            "21": sensor_test_data.test_pressure.DATA,
            "22": sensor_test_data.test_relative_rotary.DATA,
            "23": sensor_test_data.test_switch.DATA,
            "24": sensor_test_data.test_temperature.DATA,
            "25": sensor_test_data.test_thermostat.DATA,
            "26": sensor_test_data.test_time.DATA,
            "27": sensor_test_data.test_vibration.DATA,
            "28": sensor_test_data.test_water.DATA,
        },
    )
    sensors = deconz_session.sensors
    assert len(sensors._handlers) == 29
    assert sensors["0"].type == ResourceType.ZHA_AIR_PURIFIER
    assert sensors["1"].type == ResourceType.ZHA_AIR_QUALITY
    assert sensors["2"].type == ResourceType.ZHA_ALARM
    assert sensors["3"].type == ResourceType.ZHA_ANCILLARY_CONTROL
    assert sensors["4"].type == ResourceType.ZHA_BATTERY
    assert sensors["5"].type == ResourceType.ZHA_CARBON_DIOXIDE
    assert sensors["6"].type == ResourceType.ZHA_CARBON_MONOXIDE
    assert sensors["7"].type == ResourceType.ZHA_CONSUMPTION
    assert sensors["8"].type == ResourceType.DAYLIGHT
    assert sensors["9"].type == ResourceType.ZHA_DOOR_LOCK
    assert sensors["10"].type == ResourceType.ZHA_FIRE
    assert sensors["11"].type == ResourceType.ZHA_FORMALDEHYDE
    assert sensors["12"].type == ResourceType.CLIP_GENERIC_FLAG
    assert sensors["13"].type == ResourceType.CLIP_GENERIC_STATUS
    assert sensors["14"].type == ResourceType.ZHA_HUMIDITY
    assert sensors["15"].type == ResourceType.ZHA_LIGHT_LEVEL
    assert sensors["16"].type == ResourceType.ZHA_MOISTURE
    assert sensors["17"].type == ResourceType.ZHA_OPEN_CLOSE
    assert sensors["18"].type == ResourceType.ZHA_PARTICULATE_MATTER
    assert sensors["19"].type == ResourceType.ZHA_POWER
    assert sensors["20"].type == ResourceType.ZHA_PRESENCE
    assert sensors["21"].type == ResourceType.ZHA_PRESSURE
    assert sensors["22"].type == ResourceType.ZHA_RELATIVE_ROTARY
    assert sensors["23"].type == ResourceType.ZHA_SWITCH
    assert sensors["24"].type == ResourceType.ZHA_TEMPERATURE
    assert sensors["25"].type == ResourceType.ZHA_THERMOSTAT
    assert sensors["26"].type == ResourceType.ZHA_TIME
    assert sensors["27"].type == ResourceType.ZHA_VIBRATION
    assert sensors["28"].type == ResourceType.ZHA_WATER
