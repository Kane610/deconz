import aiohttp
import asyncio
import async_timeout
import logging

_LOGGER = logging.getLogger(__name__)


@asyncio.coroutine
def get_api_key(loop, host, port, username, password, **kwargs):
    """
    """
    url = 'http://' + host + ':' + str(port) + '/api'
    auth = aiohttp.BasicAuth(username, password=password)
    data = b'{"devicetype": "pydeconz"}'
    session = aiohttp.ClientSession(loop=loop)
    response = yield from request(session.post, url, auth=auth, data=data)
    yield from session.close()
    if response:
        api_key = response[0]['success']['username']
        _LOGGER.info('API key: %s', api_key)
        return api_key
    else:
        return False


@asyncio.coroutine
def delete_api_key(loop, host, port, api_key, **kwargs):
    """
    """
    url = 'http://' + host + ':' + str(port) + '/api' + api_key + '/config/whitelist/' + api_key
    session = aiohttp.ClientSession(loop=loop)
    response = yield from request(session.delete, url)
    yield from session.close()
    if response:
        _LOGGER.info(response)


@asyncio.coroutine
def delete_all_keys(loop, host, port, api_key, **kwargs):
    """
    """
    url = 'http://' + host + ':' + str(port) + '/api' + api_key + '/config'
    session = aiohttp.ClientSession(loop=loop)
    response = yield from request(session.get, url)
    yield from session.close()
    for key, _ in response['whitelist'].items():
        if key != api_key:
            yield from delete_api_key(loop, host, port, key)


@asyncio.coroutine
def request(session, url, **kwargs):
    """
    """
    try:
        with async_timeout.timeout(10):
            response = yield from session(url, **kwargs)
        if response.status != 200:
            _LOGGER.error("HTTP status %d, response %s.",
                          response.status, (yield from response.text()))
            return False
        result = yield from response.json()
    except asyncio.TimeoutError:
        _LOGGER.error("Timeout getting DeConz data from %s.", url)
        return False
    except aiohttp.ClientError:
        _LOGGER.exception("Error getting DeConz data from %s.", url)
        return False
    finally:
        #if response:
        #    yield from response.release()
        return result
