"""Python library to connect deCONZ and Home Assistant to work together."""

from typing import TypedDict, cast

from . import DeconzSensor


class TypedGenericStatusState(TypedDict):
    """Generic status state type definition."""

    status: str


class TypedGenericStatus(TypedDict):
    """Generic status type definition."""

    state: TypedGenericStatusState


class GenericStatus(DeconzSensor):
    """Generic status sensor."""

    ZHATYPE = ("CLIPGenericStatus",)

    def post_init(self) -> None:
        """Post init method."""
        self._raw = cast(TypedGenericStatus, self.raw)

    @property
    def status(self) -> str:
        """Status."""
        return self._raw["state"]["status"]
