"""Python library to connect deCONZ and Home Assistant to work together."""

from typing import TypedDict, cast

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

    def post_init(self) -> None:
        """Post init method."""
        self._raw = cast(TypedGenericFlag, self.raw)

    @property
    def flag(self) -> bool:
        """Flag status."""
        return self._raw["state"]["flag"]
