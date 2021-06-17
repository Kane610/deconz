"""Python library to connect deCONZ and Home Assistant to work together."""

import logging
from typing import Callable, Optional

from .api import APIItem

LOGGER = logging.getLogger(__name__)


class DeconzDevice(APIItem):
    """deCONZ resource base representation.

    Dresden Elektroniks REST API documentation
    http://dresden-elektronik.github.io/deconz-rest-doc/
    """

    def __init__(
        self, resource_id: str, raw: dict, request: Callable[..., Optional[dict]]
    ) -> None:
        """Set initial information common to all device types."""
        super().__init__(raw, request)
        self.resource_id = resource_id

    @property
    def resource_type(self) -> str:
        """Resource type, e.g. groups/lights/sensors."""

    @property
    def deconz_id(self) -> str:
        """Id to call device over API e.g. /sensors/1."""
        return f"/{self.resource_type}/{self.resource_id}"

    async def async_set_config(self, data: dict) -> None:
        """Set config of device."""
        field = f"{self.deconz_id}/config"
        await self.async_set(field, data)

    async def async_set_state(self, data: dict) -> None:
        """Set state of device."""
        field = f"{self.deconz_id}/state"
        await self.async_set(field, data)

    @property
    def etag(self) -> Optional[str]:
        """HTTP etag change on any action to the device."""
        return self.raw.get("etag")

    @property
    def manufacturer(self) -> str:
        """Device manufacturer."""
        return self.raw.get("manufacturername", "")

    @property
    def modelid(self) -> Optional[str]:
        """Device model."""
        return self.raw.get("modelid")

    @property
    def name(self) -> Optional[str]:
        """Name of the device."""
        return self.raw.get("name")

    @property
    def swversion(self) -> Optional[str]:
        """Firmware version."""
        return self.raw.get("swversion")

    @property
    def type(self) -> Optional[str]:
        """Human readable type of the device."""
        return self.raw.get("type")

    @property
    def uniqueid(self) -> Optional[str]:
        """Id for unique device identification."""
        return self.raw.get("uniqueid")
