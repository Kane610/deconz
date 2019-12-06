import logging

from pprint import pformat

LOGGER = logging.getLogger(__name__)


class APIItems:
    """Base class for a map of API Items."""

    # def __init__(self, raw, request, path, item_cls) -> None:
    def __init__(self, raw, loop, get, put, path, item_cls) -> None:
        # self._request = request
        self._loop = loop
        self._get = get
        self._put = put
        self._path = path
        self._item_cls = item_cls
        self._items = {}
        self.process_raw(raw)
        LOGGER.debug(pformat(raw))

    def update(self) -> None:
        # raw = self._request('get', self._path)
        raw = self._get(self._path)
        self.process_raw(raw)

    def process_raw(self, raw: dict) -> None:
        for id, raw_item in raw.items():
            obj = self._items.get(id)

            if obj is not None:
                obj.async_update(raw_item)
            else:
                self._items[id] = self._item_cls(id, raw_item, self._loop, self._put)

    def items(self):
        return self._items.items()

    def keys(self):
        return self._items.keys()

    def values(self):
        return self._items.values()

    def __getitem__(self, obj_id: str):
        return self._items[obj_id]

    def __iter__(self):
        return iter(self._items)
