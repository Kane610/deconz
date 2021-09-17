"""Python library to connect deCONZ and Home Assistant to work together."""

import logging
from typing import Optional

from .api import APIItem

LOGGER = logging.getLogger(__name__)


class DeconzDevice(APIItem):
    """deCONZ resource base representation.

    Dresden Elektroniks REST API documentation
    http://dresden-elektronik.github.io/deconz-rest-doc/
    """

    @property
    def resource_type(self) -> str:
        """Resource type, e.g. alarmsystems/groups/lights/scenes/sensors."""

    @property
    def deconz_id(self) -> str:
        """Id to call device over API e.g. /sensors/1."""
        return f"/{self.resource_type}/{self.resource_id}"

    @property
    def etag(self) -> Optional[str]:
        """HTTP etag change on any action to the device."""
        return self.raw.get("etag")

    @property
    def manufacturer(self) -> str:
        """Device manufacturer."""
        return self.raw.get("manufacturername", "")

    @property
    def model_id(self) -> Optional[str]:
        """Device model."""
        return self.raw.get("modelid")

    @property
    def name(self) -> Optional[str]:
        """Name of the device."""
        return self.raw.get("name")

    @property
    def software_version(self) -> Optional[str]:
        """Firmware version."""
        return self.raw.get("swversion")

    @property
    def type(self) -> Optional[str]:
        """Human readable type of the device."""
        return self.raw.get("type")

    @property
    def unique_id(self) -> Optional[str]:
        """Id for unique device identification."""
        return self.raw.get("uniqueid")
