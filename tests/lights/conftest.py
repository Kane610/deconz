"""Setup common light test helpers."""

import pytest


@pytest.fixture()
def deconz_light(deconz_refresh_state):
    """Comfort fixture to initialize deCONZ light."""

    async def data_to_deconz_session(light):
        """Initialize deCONZ light."""
        deconz_session = await deconz_refresh_state(lights={"0": light})
        return deconz_session.lights["0"]

    return data_to_deconz_session
