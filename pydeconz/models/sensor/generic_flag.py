"""Python library to connect deCONZ and Home Assistant to work together."""

from typing import TypedDict

from . import DeconzSensor


class TypedGenericFlagState(TypedDict):
    """Generic flag state type definition."""

    flag: bool


class TypedGenericFlag(TypedDict):
    """Generic flag type definition."""

    state: TypedGenericFlagState


class GenericFlag(DeconzSensor):
    """Generic flag sensor."""

    ZHATYPE = ("CLIPGenericFlag",)

    raw: TypedGenericFlag

    @property
    def flag(self) -> bool:
        """Flag status."""
        return self.raw["state"]["flag"]
