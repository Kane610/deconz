"""Test pydeCONZ alarm systems.

pytest --cov-report term-missing --cov=pydeconz.alarm_system tests/test_alarm_system.py
"""
from unittest.mock import AsyncMock

from pydeconz.alarm_system import (
    ArmMode,
    ArmState,
    AlarmSystems,
    DeviceTrigger,
    RESOURCE_TYPE,
)


async def test_create_alarm_system():
    """Verify that alarm system works."""
    alarm_systems = AlarmSystems(
        {
            "0": {
                "name": "default",
                "config": {
                    "armmode": "armed_away",
                    "configured": True,
                    "disarmed_entry_delay": 0,
                    "disarmed_exit_delay": 0,
                    "armed_away_entry_delay": 120,
                    "armed_away_exit_delay": 120,
                    "armed_away_trigger_duration": 120,
                    "armed_stay_entry_delay": 120,
                    "armed_stay_exit_delay": 120,
                    "armed_stay_trigger_duration": 120,
                    "armed_night_entry_delay": 120,
                    "armed_night_exit_delay": 120,
                    "armed_night_trigger_duration": 120,
                },
                "state": {"armstate": "armed_away", "seconds_remaining": 0},
                "devices": {
                    "ec:1b:bd:ff:fe:6f:c3:4d-01-0501": {"armmask": "none"},
                    "00:15:8d:00:02:af:95:f9-01-0101": {
                        "armmask": "AN",
                        "trigger": "state/vibration",
                    },
                },
            }
        },
        AsyncMock(),
    )

    await alarm_systems.create_alarm_system(name="not_default")
    alarm_systems._request.assert_called_with(
        "post",
        path="/alarmsystems",
        json={"name": "not_default"},
    )

    alarm_system_0 = alarm_systems["0"]

    assert alarm_system_0.resource_type == RESOURCE_TYPE
    assert alarm_system_0.deconz_id == "/alarmsystems/0"
    assert alarm_system_0.arm_state == ArmState.ARMED_AWAY
    assert alarm_system_0.seconds_remaining == 0
    assert alarm_system_0.pin_configured
    assert alarm_system_0.arm_mode == ArmMode.ARMED_AWAY
    assert alarm_system_0.armed_away_entry_delay == 120
    assert alarm_system_0.armed_away_exit_delay == 120
    assert alarm_system_0.armed_away_trigger_duration == 120
    assert alarm_system_0.armed_night_entry_delay == 120
    assert alarm_system_0.armed_night_exit_delay == 120
    assert alarm_system_0.armed_night_trigger_duration == 120
    assert alarm_system_0.armed_stay_entry_delay == 120
    assert alarm_system_0.armed_stay_exit_delay == 120
    assert alarm_system_0.armed_stay_trigger_duration == 120
    assert alarm_system_0.disarmed_entry_delay == 0
    assert alarm_system_0.disarmed_exit_delay == 0
    assert alarm_system_0.devices == {
        "ec:1b:bd:ff:fe:6f:c3:4d-01-0501": {"armmask": "none"},
        "00:15:8d:00:02:af:95:f9-01-0101": {
            "armmask": "AN",
            "trigger": "state/vibration",
        },
    }

    await alarm_system_0.arm_away(pin_code="1234")
    alarm_system_0._request.assert_called_with(
        "put", path="/alarmsystems/0/arm_away", json={"code0": "1234"}
    )

    await alarm_system_0.arm_night(pin_code="23456")
    alarm_system_0._request.assert_called_with(
        "put", path="/alarmsystems/0/arm_night", json={"code0": "23456"}
    )

    await alarm_system_0.arm_stay(pin_code="345678")
    alarm_system_0._request.assert_called_with(
        "put", path="/alarmsystems/0/arm_stay", json={"code0": "345678"}
    )

    await alarm_system_0.disarm(pin_code="4567890")
    alarm_system_0._request.assert_called_with(
        "put", path="/alarmsystems/0/disarm", json={"code0": "4567890"}
    )

    await alarm_system_0.set_alarm_system_configuration(
        code0="0000",
        armed_away_entry_delay=0,
        armed_away_exit_delay=1,
        armed_away_trigger_duration=2,
        armed_night_entry_delay=3,
        armed_night_exit_delay=4,
        armed_night_trigger_duration=5,
        armed_stay_entry_delay=6,
        armed_stay_exit_delay=7,
        armed_stay_trigger_duration=8,
        disarmed_entry_delay=9,
        disarmed_exit_delay=10,
    )
    alarm_system_0._request.assert_called_with(
        "put",
        path="/alarmsystems/0/config",
        json={
            "code0": "0000",
            "armed_away_entry_delay": 0,
            "armed_away_exit_delay": 1,
            "armed_away_trigger_duration": 2,
            "armed_night_entry_delay": 3,
            "armed_night_exit_delay": 4,
            "armed_night_trigger_duration": 5,
            "armed_stay_entry_delay": 6,
            "armed_stay_exit_delay": 7,
            "armed_stay_trigger_duration": 8,
            "disarmed_entry_delay": 9,
            "disarmed_exit_delay": 10,
        },
    )

    await alarm_system_0.set_alarm_system_configuration(
        code0="4444",
    )
    alarm_system_0._request.assert_called_with(
        "put",
        path="/alarmsystems/0/config",
        json={"code0": "4444"},
    )

    await alarm_system_0.add_device(
        unique_id="00:00:00:00:00:00:00:01-01-0101",
        armed_away=True,
        armed_night=True,
        armed_stay=True,
        trigger=DeviceTrigger.ON.value,
    )
    alarm_system_0._request.assert_called_with(
        "put",
        path="/alarmsystems/0/device/00:00:00:00:00:00:00:01-01-0101",
        json={"armmask": "ANS", "trigger": "state/on"},
    )

    await alarm_system_0.add_device(
        unique_id="00:00:00:00:00:00:00:01-01-0101",
        armed_night=True,
    )
    alarm_system_0._request.assert_called_with(
        "put",
        path="/alarmsystems/0/device/00:00:00:00:00:00:00:01-01-0101",
        json={"armmask": "N"},
    )

    await alarm_system_0.add_device(
        unique_id="00:00:00:00:00:00:00:01-01-0101",
        armed_stay=True,
        is_keypad=True,
    )
    alarm_system_0._request.assert_called_with(
        "put",
        path="/alarmsystems/0/device/00:00:00:00:00:00:00:01-01-0101",
        json={},
    )

    await alarm_system_0.remove_device(unique_id="00:00:00:00:00:00:00:01-01-0101")
    alarm_system_0._request.assert_called_with(
        "delete",
        path="/alarmsystems/0/device/00:00:00:00:00:00:00:01-01-0101",
    )
