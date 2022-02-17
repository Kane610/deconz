"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, Final

from ..models import ResourceTypes
from ..models.group import Group
from .api import APIItems

URL: Final = "/groups"


class Groups(APIItems[Group]):
    """Represent deCONZ groups."""

    resource_type = ResourceTypes.GROUP

    def __init__(
        self,
        raw: dict,
        request: Callable[..., Awaitable[dict[str, Any]]],
    ) -> None:
        """Initialize group manager."""
        super().__init__(raw, request, URL, Group)
