"""Setup for pydeCONZ."""

from setuptools import setup

setup(
    name="pydeconz",
    packages=["pydeconz"],
    version="87",
    description="A Python library for communicating with deCONZ REST-API from Dresden Elektronik",
    author="Robert Svensson",
    author_email="Kane610@users.noreply.github.com",
    license="MIT",
    url="https://github.com/Kane610/deconz",
    download_url="https://github.com/Kane610/deconz/archive/v87.tar.gz",
    install_requires=["aiohttp"],
    tests_require=["pytest-aiohttp", "pytest", "aioresponses"],
    keywords=["deconz", "zigbee", "homeassistant"],
    classifiers=["Natural Language :: English", "Programming Language :: Python :: 3"],
    python_requires=">=3.9.0",
)
