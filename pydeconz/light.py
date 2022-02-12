"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, Final

from .api import APIItems
from .models.light import *  # noqa: F401, F403
from .models.light import ConfigurationTool, Cover, DeconzLight, Fan, Light, Lock, Siren

URL: Final = "/lights"
NON_LIGHT_CLASSES = (ConfigurationTool, Cover, Fan, Lock, Siren)


class Lights(APIItems):
    """Represent deCONZ lights."""

    def __init__(
        self,
        raw: dict,
        request: Callable[..., Awaitable[dict[str, Any]]],
    ) -> None:
        """Initialize light manager."""
        super().__init__(raw, request, URL, create_light)


def create_light(
    light_id: str,
    raw: dict,
    request: Callable[..., Awaitable[dict[str, Any]]],
) -> DeconzLight:
    # ) -> Union[Light, ConfigurationTool, Cover, Fan, Lock, Siren]:
    """Create device out of a light resource."""
    for non_light_class in NON_LIGHT_CLASSES:
        if raw["type"] in non_light_class.ZHATYPE:
            return non_light_class(light_id, raw, request)

    return Light(light_id, raw, request)
