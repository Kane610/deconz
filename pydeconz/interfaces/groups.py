"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from ..models import ResourceGroup, ResourceType
from ..models.group import Group
from .api import APIItems


class Groups(APIItems[Group]):
    """Represent deCONZ groups."""

    resource_group = ResourceGroup.GROUP
    resource_type = ResourceType.GROUP
    item_cls = Group
