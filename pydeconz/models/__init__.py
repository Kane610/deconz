"""Data models."""

from typing import TypeVar

from .api import APIItem

DataResource = TypeVar("DataResource", bound=APIItem)
