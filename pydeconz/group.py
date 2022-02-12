"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, Final

from .api import APIItems
from .models.group import *  # noqa: F401, F403
from .models.group import Group

URL: Final = "/groups"


class Groups(APIItems):
    """Represent deCONZ groups."""

    def __init__(
        self,
        raw: dict,
        request: Callable[..., Awaitable[dict[str, Any]]],
    ) -> None:
        """Initialize group manager."""
        super().__init__(raw, request, URL, Group)
