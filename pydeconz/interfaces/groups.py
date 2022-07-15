"""Python library to connect deCONZ and Home Assistant to work together."""

from __future__ import annotations

from typing import Any

from ..models import ResourceGroup, ResourceType
from ..models.group import Group
from ..models.light.light import LightAlert, LightEffect
from .api_handlers import APIHandler


class GroupHandler(APIHandler[Group]):
    """Represent deCONZ groups."""

    resource_group = ResourceGroup.GROUP
    resource_type = ResourceType.GROUP
    item_cls = Group

    async def set_attributes(
        self,
        id: str,
        hidden: bool | None = None,
        light_sequence: list[str] | None = None,
        lights: list[str] | None = None,
        multi_device_ids: list[str] | None = None,
        name: str | None = None,
    ) -> dict[str, Any]:
        """Change attributes of a group.

        Supported values:
        - hidden [bool] Indicates the hidden status of the group
        - light_sequence [list of light IDs] Specify a sorted list of light IDs for apps
        - lights [list of light IDs]IDs of the lights which are members of the group
        - multi_device_ids [int] Subsequential light IDs of multidevices
        - name [str] The name of the group
        """
        data = {
            key: value
            for key, value in {
                "hidden": hidden,
                "lightsequence": light_sequence,
                "lights": lights,
                "multideviceids": multi_device_ids,
                "name": name,
            }.items()
            if value is not None
        }
        return await self.gateway.request(
            "put",
            path=f"{self.path}/{id}",
            json=data,
        )

    async def set_state(
        self,
        id: str,
        alert: LightAlert | None = None,
        brightness: int | None = None,
        color_loop_speed: int | None = None,
        color_temperature: int | None = None,
        effect: LightEffect | None = None,
        hue: int | None = None,
        on: bool | None = None,
        on_time: int | None = None,
        saturation: int | None = None,
        toggle: bool | None = None,
        transition_time: int | None = None,
        xy: tuple[float, float] | None = None,
    ) -> dict[str, Any]:
        """Change state of a group.

        Supported values:
        - alert [str]
          - "none" light is not performing an alert
          - "select" light is blinking a short time
          - "lselect" light is blinking a longer time
        - brightness [int] 0-255
        - color_loop_speed [int] 1-255
          - 1 = very fast
          - 15 is default
          - 255 very slow
        - color_temperature [int] between ctmin-ctmax
        - effect [str]
          - "none" no effect
          - "colorloop" the light will cycle continuously through all
                        colors with the speed specified by colorloopspeed
        - hue [int] 0-65535
        - on [bool] True/False
        - on_time [int] 0-65535 1/10 seconds resolution
        - saturation [int] 0-255
        - toggle [bool] True toggles the lights of that group from on to off
                        or vice versa, false has no effect
        - transition_time [int] 0-65535 1/10 seconds resolution
        - xy [tuple] (0-1, 0-1)
        """
        data: dict[str, Any] = {
            key: value
            for key, value in {
                "bri": brightness,
                "colorloopspeed": color_loop_speed,
                "ct": color_temperature,
                "hue": hue,
                "on": on,
                "ontime": on_time,
                "sat": saturation,
                "toggle": toggle,
                "transitiontime": transition_time,
                "xy": xy,
            }.items()
            if value is not None
        }
        if alert is not None:
            data["alert"] = alert.value
        if effect is not None:
            data["effect"] = effect.value
        return await self.gateway.request_with_retry(
            "put",
            path=f"{self.path}/{id}/action",
            json=data,
        )
