"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from typing import Final

from ..models import ResourceTypes
from ..models.group import Group
from .api import APIItems

URL: Final = "/groups"


class Groups(APIItems[Group]):
    """Represent deCONZ groups."""

    resource_type = ResourceTypes.GROUP
    path = URL
    item_cls = Group
