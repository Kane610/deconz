"""Setup common sensor test helpers."""

import pytest


@pytest.fixture()
def deconz_sensor(deconz_refresh_state):
    """Comfort fixture to initialize deCONZ sensor."""

    async def data_to_deconz_session(sensor):
        """Initialize deCONZ sensor."""
        deconz_session = await deconz_refresh_state(sensors={"0": sensor})
        return deconz_session.sensors["0"]

    return data_to_deconz_session
