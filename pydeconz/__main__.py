""""""

import aiohttp
import asyncio

from pydeconz import DeconzSession
from pydeconz.utils import (async_get_api_key, async_delete_all_keys)


@asyncio.coroutine
def main(loop, **kwargs):
    """
    """
    if 'api_key' not in kwargs:
        api_key = yield from async_get_api_key(loop, **kwargs)
        kwargs['api_key'] = api_key
        print(api_key)
    websession = aiohttp.ClientSession(loop=loop)
    deconz = DeconzSession(loop, websession, **kwargs)
    result = yield from deconz.async_load_parameters()
    if result is False:
        print('Failed to setup deCONZ')
        return False
    deconz.start()
    from pprint import pprint
    for dev_id, dev in deconz.sensors.items():
        pprint(dev.__dict__)
    # yield from deconz.close()
    # yield from async_delete_api_key(loop, **kwargs)


kw = {'host': '127.0.0.1',
      'port': 80,
      'api_key': '501AF019AB',
      'username': 'delight',
      'password': 'delight'
      }

loop = asyncio.get_event_loop()
loop.run_until_complete(main(loop, **kw))
loop.run_forever()
loop.close()
