"""Python library to connect deCONZ and Home Assistant to work together."""

from typing import NotRequired, TypeVar

from .api import ApiData, APIItem


class TypedData(ApiData):
    """Scene type definition."""

    etag: NotRequired[str]
    manufacturername: NotRequired[str]
    modelid: NotRequired[str]
    name: NotRequired[str]
    swversion: NotRequired[str]
    type: NotRequired[str]
    uniqueid: NotRequired[str]


ApiDataT = TypeVar("ApiDataT", bound=TypedData)


class DeconzDevice(APIItem[ApiDataT]):
    # class DeconzDevice(APIItem[ApiDataT], Generic[ApiDataT]):
    """deCONZ resource base representation.

    Dresden Elektroniks REST API documentation
    http://dresden-elektronik.github.io/deconz-rest-doc/
    """

    raw: ApiDataT

    @property
    def etag(self) -> str:
        """HTTP etag change on any action to the device."""
        # raw: dict[str, str] = self.raw
        if "etag" in self.raw:
            return self.raw["etag"]
        return ""

    @property
    def manufacturer(self) -> str:
        """Device manufacturer."""
        if "manufacturername" in self.raw:
            return self.raw["manufacturername"]
        return ""

    @property
    def model_id(self) -> str:
        """Device model."""
        if "modelid" in self.raw:
            return self.raw["modelid"]
        return ""

    @property
    def name(self) -> str:
        """Name of the device."""
        if "name" in self.raw:
            return self.raw["name"]
        return ""

    @property
    def software_version(self) -> str:
        """Firmware version."""
        if "swversion" in self.raw:
            return self.raw["swversion"]
        return ""

    @property
    def type(self) -> str:
        """Human readable type of the device."""
        if "type" in self.raw:
            return self.raw["type"]
        return ""

    @property
    def unique_id(self) -> str:
        """Id for unique device identification."""
        if "uniqueid" in self.raw:
            return self.raw["uniqueid"]
        return ""
