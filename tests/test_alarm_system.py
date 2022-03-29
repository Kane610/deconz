"""Test pydeCONZ alarm systems.

pytest --cov-report term-missing --cov=pydeconz.alarm_system tests/test_alarm_system.py
"""

from pydeconz.interfaces.alarm_systems import ArmAction, DeviceTrigger
from pydeconz.models.alarm_system import (
    ARM_MODE_ARMED_AWAY,
    ARM_STATE_ARMED_AWAY,
    DEVICE_TRIGGER_ON,
    RESOURCE_TYPE,
)


async def test_create_alarm_system(
    mock_aioresponse, deconz_refresh_state, deconz_called_with
):
    """Verify that alarm system works."""

    deconz_session = await deconz_refresh_state(
        alarm_systems={
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
        }
    )

    alarm_systems = deconz_session.alarmsystems

    assert len(alarm_systems.keys()) == 1

    mock_aioresponse.post("http://host:80/api/apikey/alarmsystems")
    await alarm_systems.create_alarm_system(name="not_default")
    assert deconz_called_with(
        "post",
        path="/alarmsystems",
        json={"name": "not_default"},
    )

    mock_aioresponse.put("http://host:80/api/apikey/alarmsystems/0/arm_away")
    await alarm_systems.arm(id="0", action=ArmAction.AWAY, pin_code="1234")
    assert deconz_called_with(
        "put", path="/alarmsystems/0/arm_away", json={"code0": "1234"}
    )

    mock_aioresponse.put("http://host:80/api/apikey/alarmsystems/0/arm_night")
    await alarm_systems.arm(id="0", action=ArmAction.NIGHT, pin_code="23456")
    assert deconz_called_with(
        "put", path="/alarmsystems/0/arm_night", json={"code0": "23456"}
    )

    mock_aioresponse.put("http://host:80/api/apikey/alarmsystems/0/arm_stay")
    await alarm_systems.arm(id="0", action=ArmAction.STAY, pin_code="345678")
    assert deconz_called_with(
        "put", path="/alarmsystems/0/arm_stay", json={"code0": "345678"}
    )

    mock_aioresponse.put("http://host:80/api/apikey/alarmsystems/0/disarm")
    await alarm_systems.arm(id="0", action=ArmAction.DISARM, pin_code="4567890")
    assert deconz_called_with(
        "put", path="/alarmsystems/0/disarm", json={"code0": "4567890"}
    )

    mock_aioresponse.put("http://host:80/api/apikey/alarmsystems/0/config")
    await alarm_systems.set_alarm_system_configuration(
        id="0",
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
    assert deconz_called_with(
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

    mock_aioresponse.put("http://host:80/api/apikey/alarmsystems/0/config")
    await alarm_systems.set_alarm_system_configuration(
        id="0",
        code0="4444",
    )
    assert deconz_called_with(
        "put",
        path="/alarmsystems/0/config",
        json={"code0": "4444"},
    )

    mock_aioresponse.put(
        "http://host:80/api/apikey/alarmsystems/0/device/00:00:00:00:00:00:00:01-01-0101"
    )
    await alarm_systems.add_device(
        id="0",
        unique_id="00:00:00:00:00:00:00:01-01-0101",
        armed_away=True,
        armed_night=True,
        armed_stay=True,
        trigger=DeviceTrigger.ON,
    )
    assert deconz_called_with(
        "put",
        path="/alarmsystems/0/device/00:00:00:00:00:00:00:01-01-0101",
        json={"armmask": "ANS", "trigger": "state/on"},
    )

    mock_aioresponse.put(
        "http://host:80/api/apikey/alarmsystems/0/device/00:00:00:00:00:00:00:01-01-0101"
    )
    await alarm_systems.add_device(
        id="0",
        unique_id="00:00:00:00:00:00:00:01-01-0101",
        armed_night=True,
    )
    assert deconz_called_with(
        "put",
        path="/alarmsystems/0/device/00:00:00:00:00:00:00:01-01-0101",
        json={"armmask": "N"},
    )

    mock_aioresponse.put(
        "http://host:80/api/apikey/alarmsystems/0/device/00:00:00:00:00:00:00:01-01-0101"
    )
    await alarm_systems.add_device(
        id="0",
        unique_id="00:00:00:00:00:00:00:01-01-0101",
        armed_stay=True,
        is_keypad=True,
    )
    assert deconz_called_with(
        "put",
        path="/alarmsystems/0/device/00:00:00:00:00:00:00:01-01-0101",
        json={},
    )

    mock_aioresponse.delete(
        "http://host:80/api/apikey/alarmsystems/0/device/00:00:00:00:00:00:00:01-01-0101"
    )
    await alarm_systems.remove_device(
        id="0",
        unique_id="00:00:00:00:00:00:00:01-01-0101",
    )
    assert deconz_called_with(
        "delete",
        path="/alarmsystems/0/device/00:00:00:00:00:00:00:01-01-0101",
        json=None,
    )

    # Test model

    alarm_system_0 = alarm_systems["0"]

    assert alarm_system_0.resource_type == RESOURCE_TYPE
    assert alarm_system_0.deconz_id == "/alarmsystems/0"
    assert alarm_system_0.arm_state == ARM_STATE_ARMED_AWAY
    assert alarm_system_0.seconds_remaining == 0
    assert alarm_system_0.pin_configured
    assert alarm_system_0.arm_mode == ARM_MODE_ARMED_AWAY
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

    mock_aioresponse.put("http://host:80/api/apikey/alarmsystems/0/arm_away")
    await alarm_system_0.arm_away(pin_code="1234")
    assert deconz_called_with(
        "put", path="/alarmsystems/0/arm_away", json={"code0": "1234"}
    )

    mock_aioresponse.put("http://host:80/api/apikey/alarmsystems/0/arm_night")
    await alarm_system_0.arm_night(pin_code="23456")
    assert deconz_called_with(
        "put", path="/alarmsystems/0/arm_night", json={"code0": "23456"}
    )

    mock_aioresponse.put("http://host:80/api/apikey/alarmsystems/0/arm_stay")
    await alarm_system_0.arm_stay(pin_code="345678")
    assert deconz_called_with(
        "put", path="/alarmsystems/0/arm_stay", json={"code0": "345678"}
    )

    mock_aioresponse.put("http://host:80/api/apikey/alarmsystems/0/disarm")
    await alarm_system_0.disarm(pin_code="4567890")
    assert deconz_called_with(
        "put", path="/alarmsystems/0/disarm", json={"code0": "4567890"}
    )

    mock_aioresponse.put("http://host:80/api/apikey/alarmsystems/0/config")
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
    assert deconz_called_with(
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

    mock_aioresponse.put("http://host:80/api/apikey/alarmsystems/0/config")
    await alarm_system_0.set_alarm_system_configuration(
        code0="4444",
    )
    assert deconz_called_with(
        "put",
        path="/alarmsystems/0/config",
        json={"code0": "4444"},
    )

    mock_aioresponse.put(
        "http://host:80/api/apikey/alarmsystems/0/device/00:00:00:00:00:00:00:01-01-0101"
    )
    await alarm_system_0.add_device(
        unique_id="00:00:00:00:00:00:00:01-01-0101",
        armed_away=True,
        armed_night=True,
        armed_stay=True,
        trigger=DEVICE_TRIGGER_ON,
    )
    assert deconz_called_with(
        "put",
        path="/alarmsystems/0/device/00:00:00:00:00:00:00:01-01-0101",
        json={"armmask": "ANS", "trigger": "state/on"},
    )

    mock_aioresponse.put(
        "http://host:80/api/apikey/alarmsystems/0/device/00:00:00:00:00:00:00:01-01-0101"
    )
    await alarm_system_0.add_device(
        unique_id="00:00:00:00:00:00:00:01-01-0101",
        armed_night=True,
    )
    assert deconz_called_with(
        "put",
        path="/alarmsystems/0/device/00:00:00:00:00:00:00:01-01-0101",
        json={"armmask": "N"},
    )

    mock_aioresponse.put(
        "http://host:80/api/apikey/alarmsystems/0/device/00:00:00:00:00:00:00:01-01-0101"
    )
    await alarm_system_0.add_device(
        unique_id="00:00:00:00:00:00:00:01-01-0101",
        armed_stay=True,
        is_keypad=True,
    )
    assert deconz_called_with(
        "put",
        path="/alarmsystems/0/device/00:00:00:00:00:00:00:01-01-0101",
        json={},
    )

    mock_aioresponse.delete(
        "http://host:80/api/apikey/alarmsystems/0/device/00:00:00:00:00:00:00:01-01-0101"
    )
    await alarm_system_0.remove_device(unique_id="00:00:00:00:00:00:00:01-01-0101")
    assert deconz_called_with(
        "delete",
        path="/alarmsystems/0/device/00:00:00:00:00:00:00:01-01-0101",
        json=None,
    )
