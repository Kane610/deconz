import asyncio

from pydeconz import DeconzSession
from pydeconz.utils import (get_api_key, delete_all_keys)
from .websocket import WSClient

@asyncio.coroutine
def main(loop, **kwargs):
    """
    """
    if 'api_key' not in kwargs:
        api_key = yield from get_api_key(loop, **kwargs)
        kwargs['api_key'] = api_key
        print(api_key)

    deconz = DeconzSession(loop, **kwargs)
    result = yield from deconz.populate_config()
    result = yield from deconz.populate_lights()
    result = yield from deconz.populate_sensors()
    deconz.start()
#    print(deconz.lights)
#    field = '/lights/1/state'
#    data = {'on': False}
#    yield from deconz.lights['1'].set_state(field, data)
    #while True:
    #    yield from deconz.get_event_async()
    #    pass
    #try:
    #    yield from delete_all_keys(loop, **kwargs)
    #finally:
    #    pass
#    yield from deconz.close()
    #yield from delete_api_key(loop, **kwargs)


kw = {'host': '10.0.1.16',
      'port': 80,
      'api_key': '61314EDEDA',
      'username': 'delight',
      'password': 'delight'}

loop = asyncio.get_event_loop()
loop.run_until_complete(main(loop, **kw))
# loop.call_soon(partial(main, loop, **kw))
loop.run_forever()
loop.close()
