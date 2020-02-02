"""Python library to connect deCONZ and Home Assistant to work together."""

import logging
from pprint import pformat

from .api import APIItem

LOGGER = logging.getLogger(__name__)


class DeconzDevice(APIItem):
    """deCONZ resource base representation.

    Dresden Elektroniks REST API documentation
    http://dresden-elektronik.github.io/deconz-rest-doc/
    """

    DECONZ_TYPE = ""

    def __init__(self, device_id, raw, request):
        """Set initial information common to all device types."""
        super().__init__(raw, request)
        self.device_id = device_id

        LOGGER.debug("%s created as \n%s", self.name, pformat(self.raw))

    async def async_set_config(self, data):
        """Set config of device."""
        field = f"{self.deconz_id}/config"
        await self.async_set(field, data)

    async def async_set_state(self, data: dict):
        """Set state of device."""
        field = f"{self.deconz_id}/state"
        await self.async_set(field, data)

    @property
    def deconz_id(self):
        """Id to call device over API e.g. /sensors/1."""
        return f"/{self.DECONZ_TYPE}/{self.device_id}"

    @property
    def etag(self):
        """HTTP etag change on any action to the device."""
        return self.raw.get("etag")

    @property
    def manufacturer(self):
        """Device manufacturer."""
        return self.raw.get("manufacturername", "")

    @property
    def modelid(self):
        """Device model."""
        return self.raw.get("modelid")

    @property
    def name(self):
        """Name of the device."""
        return self.raw.get("name")

    @property
    def swversion(self):
        """Firmware version."""
        return self.raw.get("swversion")

    @property
    def type(self):
        """Human readable type of the device."""
        return self.raw.get("type")

    @property
    def uniqueid(self):
        """Id for unique device identification."""
        return self.raw.get("uniqueid")
