""""""

import aiohttp
import asyncio

from pydeconz import DeconzSession
from pydeconz.utils import async_get_api_key, async_delete_all_keys


async def main(loop, **kwargs):
    """
    """
    if "api_key" not in kwargs:
        api_key = await async_get_api_key(loop, **kwargs)
        kwargs["api_key"] = api_key
        print(api_key)
    websession = aiohttp.ClientSession(loop=loop)
    deconz = DeconzSession(loop, websession, **kwargs)
    result = await deconz.async_load_parameters()
    if result is False:
        print("Failed to setup deCONZ")
        return False
    deconz.start()
    from pprint import pprint

    pprint(deconz.__dict__)
    # await deconz.async_delete_state('/lights/2/groups', {'reset':'true'})
    # for dev_id, dev in deconz.config.values():
    #    pprint(dev.__dict__)
    # await deconz.close()
    # await async_delete_api_key(loop, **kwargs)
    # await async_delete_all_keys(loop, **kwargs)


kw = {
    "host": "10.0.0.10",
    "port": 8088,
    "api_key": "8BA2DD354B",
    #'username': 'delight',
    #'password': 'delight'
}

loop = asyncio.get_event_loop()
loop.run_until_complete(main(loop, **kw))
loop.run_forever()
loop.close()
