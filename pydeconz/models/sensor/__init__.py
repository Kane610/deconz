"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from typing import Final

from ..deconz_device import DeconzDevice

RESOURCE_TYPE: Final = "sensors"


def convert_temperature(temperature: int) -> float:
    """Convert temperature to Celsius."""
    return round(float(temperature) / 100, 1)


class DeconzSensor(DeconzDevice):
    """deCONZ sensor representation.

    Dresden Elektroniks documentation of sensors in deCONZ
    http://dresden-elektronik.github.io/deconz-rest-doc/sensors/
    """

    ZHATYPE: tuple[str, ...] = ()

    @property
    def resource_type(self) -> str:
        """Resource type."""
        return RESOURCE_TYPE

    @property
    def battery(self) -> int | None:
        """Battery status of sensor."""
        if not isinstance(battery := self.raw["config"].get("battery"), int):
            return None
        return battery

    @property
    def config_pending(self) -> list[str] | None:
        """List of configurations pending device acceptance.

        Only supported by Hue devices.
        """
        if not isinstance(pending := self.raw["config"].get("pending"), list):
            return None
        return pending

    @property
    def ep(self) -> int | None:
        """Endpoint of sensor."""
        return self.raw.get("ep")

    @property
    def low_battery(self) -> bool | None:
        """Low battery."""
        if not isinstance(lowbattery := self.raw["state"].get("lowbattery"), bool):
            return None
        return lowbattery

    @property
    def on(self) -> bool | None:
        """Declare if the sensor is on or off."""
        if not isinstance(on := self.raw["config"].get("on"), bool):
            return None
        return on

    @property
    def reachable(self) -> bool:
        """Declare if the sensor is reachable."""
        if not isinstance(reachable := self.raw["config"].get("reachable"), bool):
            return True
        return reachable

    @property
    def tampered(self) -> bool | None:
        """Tampered."""
        if not isinstance(tampered := self.raw["state"].get("tampered"), bool):
            return None
        return tampered

    @property
    def secondary_temperature(self) -> float | None:
        """Extra temperature available on some Xiaomi devices."""
        if not isinstance(temperature := self.raw["config"].get("temperature"), int):
            return None

        return convert_temperature(temperature)
