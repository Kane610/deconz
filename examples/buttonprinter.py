import asyncio
import async_timeout
import aiohttp
import logging
import functools
from pydeconz import (
    DeconzSession,
    errors,
    sensor,
    websocket,
    ERRORS,
)


HOST = "192.168.0.2"   # your host goes here
PORT = "80"              # your port here 
API_KEY = "apikey" # your api key goes here see https://dresden-elektronik.github.io/deconz-rest-doc/getting_started/


LOGGER = logging.getLogger(__name__)

class ButtonPrinter:
    def buttonCallback(self, switch):
        print(f"{switch.name} : {switch.unique_id} state: {switch.state}")


async def deconz_gateway(
    session: aiohttp.ClientSession,
    host: str,
    port: int,
    api_key: str
) -> DeconzSession:
    """Create a gateway object and verify configuration."""
    deconz = DeconzSession(session, host, port, api_key)

    try:
        with async_timeout.timeout(5):
            await deconz.refresh_state()
        return deconz

    except errors.Unauthorized:
        LOGGER.exception("Invalid API key for deCONZ gateway")

    except (asyncio.TimeoutError, errors.RequestError):
        LOGGER.error("Error connecting to deCONZ gateway")

    return None


async def asyncmain():
    clsession = aiohttp.ClientSession()
    btnprinter = ButtonPrinter()
    gateway = await deconz_gateway(
        session=clsession,
        host=HOST,
        port=PORT,
        api_key=API_KEY
    )
    if not gateway:
        LOGGER.error("Couldn't connect to deCONZ gateway")
        await clsession.close()
        return

    gateway.start()


    for sensor_key in gateway.sensors:
        curr_sensor = gateway.sensors[sensor_key]
        if isinstance(curr_sensor,sensor.Switch):            
            print(f"Found Switch {curr_sensor.name} : {curr_sensor.unique_id}")
            # this effectively creates a new function which retains the curr_sensor to be passed into the method above
            curr_callback = functools.partial(btnprinter.buttonCallback,curr_sensor)
            curr_sensor.register_callback(curr_callback) 


    try:
        while True:
            await asyncio.sleep(1)
            

    except asyncio.CancelledError:
        pass

    finally:
        gateway.close()
        await clsession.close()

if __name__ == "__main__":
    asyncio.run(asyncmain())
